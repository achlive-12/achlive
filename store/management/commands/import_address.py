import csv
from django.core.management.base import BaseCommand
from payment.models import Addr
from payment.models import Balance
from accounts.models import Customer

class Command(BaseCommand):
    help = 'Import addresses from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the input CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        addresses_to_create = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                address = row['Address']
                balance_id = row['Balance']
                created_by_username = row['Created By']

                try:
                    balance = Balance.objects.get(id=balance_id)
                except Balance.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Balance with ID {balance_id} does not exist. Skipping row."))
                    continue

                try:
                    created_by = Customer.objects.filter(username=created_by_username).first()
                except Customer.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Customer {created_by_username} does not exist. Skipping row."))
                    continue

                addresses_to_create.append(Addr(
                    address=address,
                    balance=balance,
                    created_by=created_by
                ))

        Addr.objects.bulk_create(addresses_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Addresses imported successfully.'))