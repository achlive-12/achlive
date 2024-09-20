from django.core.management.base import BaseCommand
from payment.models import Addr
import csv

class Command(BaseCommand):
    help = 'Export addresses to a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the output data file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['Address', 'Balance', 'Created By']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for addr in Addr.objects.all():
                writer.writerow({
                    'Address': addr.address,
                    'Balance': addr.balance.id,  # Assuming you want to export the ID of the related Balance
                    'Created By': addr.created_by.username
                })

        self.stdout.write(self.style.SUCCESS('Addresses exported successfully.'))