from django.core.management.base import BaseCommand
from payment.models import Invoice
import csv

class Command(BaseCommand):
    help = 'Export products to a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the output data file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['status', 'order_id', 'address', 'btcvalue', 'received', 'created_by', 'product']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for invoice in Invoice.objects.all():
                writer.writerow({
                    'status': invoice.status,
                    'order_id': invoice.order_id,
                    'address': invoice.address,
                    'btcvalue': invoice.btcvalue,
                    'received': invoice.received,
                    'created_by': invoice.created_by,
                    'product': invoice.product
                })

        self.stdout.write(self.style.SUCCESS('Invoices exported successfully.'))