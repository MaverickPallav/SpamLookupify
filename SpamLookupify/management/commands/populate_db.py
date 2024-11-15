import random
from django.core.management.base import BaseCommand
from SpamLookupify.models import User, Contact, SpamReport
from faker import Faker

fake = Faker()

class Command(BaseCommand):
    help = "Populates the database with sample data."

    def handle(self, *args, **kwargs):
        # Create sample users
        for _ in range(10):
            user = User.objects.create_user(
                username=fake.user_name(),
                password="password",
                phone_number=fake.phone_number(),
                email=fake.email(),
                name=fake.name()
            )

            # Create contacts
            for _ in range(5):
                Contact.objects.create(
                    owner=user,
                    name=fake.name(),
                    phone_number=fake.phone_number()
                )

        # Create spam reports
        for _ in range(15):
            SpamReport.objects.create(phone_number=fake.phone_number(), spam_count=random.randint(1, 5))

        self.stdout.write(self.style.SUCCESS("Database populated with sample data."))