from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from SpamLookupify.models import User, Contact, SpamReport

class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'name': 'John Doe',
            'username': 'john_doe',
            'password': 'password123',
            'phone_number': '+1234567890'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_phone_number(self):
        User.objects.create_user(name='User1', username='user1', password='password123', phone_number='+1234567890')
        response = self.client.post(reverse('register'), {
            'name': 'User2',
            'username': 'user2',
            'password': 'password123',
            'phone_number': '+1234567890'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(name='User1', username='user1', password='password123', phone_number='+1234567890')

    def test_user_login_required_for_protected_endpoint(self):
        response = self.client.get(reverse('contact-list-create'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Login the user
        login_response = self.client.post(reverse('login'), {
            'username': 'user1',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Now test authenticated access
        response = self.client.get(reverse('contact-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ContactManagementTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(name='User1', username='user1', password='password123', phone_number='+1234567890')
        # Login the user
        self.client.login(username='user1', password='password123')

    def test_add_contact(self):
        response = self.client.post(reverse('contact-list-create'), {
            'name': 'Jane Doe',
            'phone_number': '+0987654321',
            'is_spam': False
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)

    def test_view_contacts(self):
        Contact.objects.create(owner=self.user, name='Jane Doe', phone_number='+0987654321')
        response = self.client.get(reverse('contact-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class SpamReportingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(name='User1', username='user1', password='password123', phone_number='+1234567890')
        # Login the user
        self.client.login(username='user1', password='password123')

    def test_report_spam(self):
        response = self.client.post(reverse('report-spam'), {
            'phone_number': '+1122334455'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        spam_report = SpamReport.objects.get(phone_number='+1122334455')
        self.assertEqual(spam_report.spam_count, 1)

class SearchFunctionalityTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(name='User1', username='user1', password='password123', phone_number='+1234567890')
        # Login the user
        self.client.login(username='user1', password='password123')
        # Adding contacts to simulate search results
        Contact.objects.create(owner=self.user, name='Alice Anderson', phone_number='+1122334455')
        Contact.objects.create(owner=self.user, name='Bob Barker', phone_number='+2233445566')

    def test_search_by_name_exact_match(self):
        response = self.client.get(reverse('search'), {'query': 'Alice'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Alice Anderson')

    def test_search_by_name_partial_match(self):
        response = self.client.get(reverse('search'), {'query': 'Al'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_phone_number(self):
        response = self.client.get(reverse('search'), {'phone_number': '+1122334455'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['phone_number'], '+1122334455')

    def test_search_by_non_existent_phone_number(self):
        response = self.client.get(reverse('search'), {'phone_number': '+0000000000'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'No contacts found.')
