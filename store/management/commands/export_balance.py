from django.core.management.base import BaseCommand
from payment.models import Balance
import csv

class Command(BaseCommand):
    help = 'Export products to a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the output data file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['order_id', 'address', 'received', 'balance', 'created_by']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for product in Balance.objects.all():
                writer.writerow({
                    'order_id': product.order_id,
                    'address': product.address,
                    'received': product.received,
                    'balance': product.balance,
                    'created_by': product.created_by
                })

        self.stdout.write(self.style.SUCCESS('Balances exported successfully.'))