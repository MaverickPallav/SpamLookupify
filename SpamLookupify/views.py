import re
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Count
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Contact, SpamReport, SpamReporters
from .serializers import UserSerializer, ContactSerializer, SpamReportSerializer
from .permissions import IsOwnerOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from .ratelimit import RegisterThrottle, LoginThrottle, LogoutThrottle, ContactThrottle, ReportSpamThrottle, SearchThrottle

def validate_phone_number(phone_number):
    phone_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_regex, phone_number):
        raise ValidationError({"error": "Invalid phone number format. Please use the format: '+999999999' or '999999999'."})

class RegisterView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    # throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    # throttle_classes = [LoginThrottle]

    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {"message": "You are already logged in."},
                status=status.HTTP_200_OK
            )

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        
        return Response({"message": "Invalid credentials. Please verify your login details or register for a new account."}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    # throttle_classes = [LogoutThrottle]

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'You are already logged out.'}, status=status.HTTP_400_BAD_REQUEST)

class ContactListCreateView(APIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    # throttle_classes = [ContactThrottle]

    def get(self, request):
        contacts = Contact.objects.filter(owner=request.user)
        serializer = self.serializer_class(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data.get('phone_number')
        existing_contact = Contact.objects.filter(owner=request.user, phone_number=phone_number).first()

        if existing_contact:
            raise ValidationError({'error': 'A contact with this phone number already exists.'})

        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class ContactDetailView(APIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    # throttle_classes = [ContactThrottle]

    def get(self, request, contact_id):
        contact = self.get_object(request, contact_id)
        serializer = self.serializer_class(contact)
        return Response(serializer.data)

    def put(self, request, contact_id):
        contact = self.get_object(request, contact_id)
        serializer = self.serializer_class(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, contact_id):
        contact = self.get_object(request, contact_id)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_object(self, request, contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)
            if request.method in permissions.SAFE_METHODS or contact.owner == request.user:
                return contact
            else:
                raise ValidationError({"error": "The requested object does not belong to you."})

        except Contact.DoesNotExist:
            raise ValidationError({'error': 'Contact not found.'})

class ReportSpamView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # throttle_classes = [ReportSpamThrottle]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        validate_phone_number(phone_number)
        
        user = User.objects.filter(phone_number=phone_number).first()

        if request.user == user:
            return Response({"error": "You are not allowed to mark your own number as spam."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contact = Contact.objects.get(phone_number=phone_number)
        except Contact.DoesNotExist:
            contact = Contact.objects.create(
                owner=request.user,         
                name="Anonymous",           
                phone_number=phone_number,
                is_anonymous=True
            )
        
        contact.is_spam = True
        contact.save()
    
        spam_report, created = SpamReport.objects.get_or_create(phone_number=phone_number)
        spam_report.increment_spam_count()
        spam_report.save()

        spam_reporter, created = SpamReporters.objects.get_or_create(phone_number=phone_number, user=request.user)
        spam_reporter.increment_report_count()
        spam_reporter.last_reported_at = timezone.now()
        spam_reporter.save()

        return Response({"message": "Marked as spam"}, status=status.HTTP_200_OK)

class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # throttle_classes = [SearchThrottle]

    def get(self, request):
        query = request.query_params.get('query')
        phone_number = request.query_params.get('phone_number')

        if not query and not phone_number:
            return Response({"error": "At least one search query is required"}, status=status.HTTP_400_BAD_REQUEST)

        if query:
            return self.filter_using_query(request, query)
        elif phone_number:
            return self.filter_using_phone_number(request, phone_number)
            
    def filter_using_query(self, request, query):
        results = []
        added_phone_numbers = set()

        users = User.objects.filter(name__icontains=query)
        requesting_user = User.objects.filter(id=request.user.id).first()
        
        for user in users:
            if user.phone_number not in added_phone_numbers:
                spam_report = SpamReport.objects.filter(phone_number=user.phone_number).first()
                spam_count = spam_report.spam_count if spam_report else 0

                user_info = {
                    "name": user.name,
                    "phone_number": user.phone_number,
                    "spam_count": spam_count,
                }

                if user.contacts.filter(phone_number=requesting_user.phone_number).exists():
                    if user.email:
                        user_info["email"] = user.email

                results.append(user_info)
                added_phone_numbers.add(user.phone_number)

        contacts = Contact.objects.filter(Q(name__istartswith=query) | Q(name__icontains=query)).distinct()
        
        for contact in contacts:
            if contact.phone_number in added_phone_numbers:
                continue

            spam_report = SpamReport.objects.filter(phone_number=contact.phone_number).first()
            spam_count = spam_report.spam_count if spam_report else 0

            contact_info = {
                "name": contact.name,
                "phone_number": contact.phone_number,
                "spam_count": spam_count
            }

            results.append(contact_info)
            added_phone_numbers.add(contact.phone_number)

        return Response(results, status=status.HTTP_200_OK)

    def filter_using_phone_number(self, request, phone_number):
        results = []

        user = User.objects.filter(phone_number=phone_number).first()
        contacts = Contact.objects.filter(phone_number=phone_number).distinct()
        requesting_user = User.objects.filter(id=request.user.id).first()

        spam_report = SpamReport.objects.filter(phone_number=phone_number).first()
        spam_count = spam_report.spam_count if spam_report else 0

        if user:
            contact_info = {
                "name": user.name,
                "phone_number": user.phone_number,
                "spam_count": spam_count
            }
            
            if request.user.contacts.filter(phone_number=phone_number).exists():
                if user.email:
                    contact_info["email"] = user.email

            results.append(contact_info)
        else:
            for contact in contacts:
                contact_info = {
                    "name": contact.name,
                    "phone_number": contact.phone_number,
                    "spam_count": spam_count
                }

                if contact.owner.contacts.filter(phone_number=requesting_user.phone_number).exists():
                    if contact.owner.email:
                        contact_info["email"] = contact.owner.email

                results.append(contact_info)

            if not results:
                return Response({"error": "No contacts found."}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(results, status=status.HTTP_200_OK)