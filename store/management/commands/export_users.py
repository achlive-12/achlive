import csv
from django.core.management.base import BaseCommand
from accounts.models import Customer

class Command(BaseCommand):
    help = 'Export products to a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the output data file')

    def handle(self, *args, **options):
        users = Customer.objects.all()

        with open(options['file_path'], 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'email', 'password', 'is_active', 'verified', 'is_staff']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for user in users:
                password_hash = user.password  # Use the existing password hash
                writer.writerow({
                    'username': user.username,
                    'email': user.email,
                    'password': password_hash,
                    'is_active': user.is_active,
                    'verified': user.verified,
                    'is_staff': user.is_staff
                })

        self.stdout.write(self.style.SUCCESS("User export complete."))