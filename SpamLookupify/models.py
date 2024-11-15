from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
import uuid

class User(AbstractUser):
    name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(
        max_length=15, unique=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    email = models.EmailField(validators=[EmailValidator(message="Enter a valid email address.")], blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    REQUIRED_FIELDS = ['phone_number', 'name']
    USERNAME_FIELD = 'username'

class Contact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    phone_number = phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    is_spam = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = ['owner', 'phone_number']

class SpamReport(models.Model):
    phone_number = models.CharField(
        max_length=15, unique=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    spam_count = models.IntegerField(default=0)
    last_reported_at = models.DateTimeField(auto_now=True)

    def increment_spam_count(self):
        self.spam_count += 1
        self.save()

class RequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    request_type = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)
    data = models.JSONField()
    request_path = models.CharField(max_length=255, default='/unknown')

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"{user_display} - {self.request_type} at {self.timestamp}"
    
class SpamReporters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    report_count = models.IntegerField(default=0)
    first_reported_at = models.DateTimeField(auto_now_add=True)
    last_reported_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'phone_number')

    def increment_report_count(self):
        self.report_count += 1
        self.save()