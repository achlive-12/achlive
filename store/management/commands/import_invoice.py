import csv
from django.core.management.base import BaseCommand
from payment.models import Invoice
from accounts.models import Customer
from store.models import Product

class Command(BaseCommand):
    help = 'Import invoices from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the input CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        invoices_to_create = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                status = row['status']
                order_id = row['order_id']
                address = row['address']
                btcvalue = row['btcvalue']
                received = row['received']
                created_by_username = row['created_by']
                product_name = row['product']

                try:
                    created_by = Customer.objects.get(username=created_by_username)
                except Customer.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Customer {created_by_username} does not exist. Skipping row."))
                    continue

                product = Product.objects.filter(name=product_name).first()
                if not product:
                    self.stdout.write(self.style.WARNING(f"Product {product_name} does not exist. Skipping row."))
                    continue

                try:
                    btcvalue = float(btcvalue)
                    received = float(received)
                except ValueError:
                    btcvalue = 1.0
                    received = 0.0

                invoices_to_create.append(Invoice(
                    status=status,
                    order_id=order_id,
                    address=address,
                    btcvalue=btcvalue,
                    received=received,
                    created_by=created_by,
                    product=product,
                    sold=True
                ))

        Invoice.objects.bulk_create(invoices_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Invoices imported successfully.'))