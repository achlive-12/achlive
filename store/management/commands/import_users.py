import csv
from accounts.models import Customer
from django.core.management.base import BaseCommand
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Import users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the input CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        users_to_create = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['username']
                email = row['email']
                password = row['password']
                is_active = row['is_active'].strip("'").lower() == 'true'
                verified = row['verified'].strip("'").lower() == 'true'
                is_staff = row['is_staff'].strip("'").lower() == 'true'

                user_data = {
                    'username': username,
                    'email': email,
                    'is_active': is_active,
                    'verified': verified,
                    'is_staff': is_staff,
                    'password': password,
                }

                users_to_create.append(Customer(**user_data))

        try:
            Customer.objects.bulk_create(users_to_create, ignore_conflicts=True)
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f"Error importing users: {e}"))

        self.stdout.write(self.style.SUCCESS("User import complete."))