import csv
from django.core.management.base import BaseCommand
from payment.models import Balance
from accounts.models import Customer

class Command(BaseCommand):
    help = 'Import balances from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the input CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        balances_to_create = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                order_id = row['order_id']
                address = row['address']
                received = row['received']
                balance = row['balance']
                created_by_username = row['created_by']

                try:
                    created_by = Customer.objects.filter(username=created_by_username).first()
                except Customer.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Customer {created_by_username} does not exist. Skipping row."))
                    continue

                try:
                    received = float(received)
                    balance = float(balance)
                except ValueError:
                    received = 0.0
                    balance = 0.0

                balances_to_create.append(Balance(
                    order_id=order_id,
                    address=address,
                    received=received,
                    balance=balance,
                    created_by=created_by
                ))

        Balance.objects.bulk_create(balances_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Balances imported successfully.'))