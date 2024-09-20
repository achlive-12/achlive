from django.core.management.base import BaseCommand
from store.models import Product
import csv

class Command(BaseCommand):
    help = 'Export products to a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the output data file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['Category', 'Name', 'Balance', 'Title', 'Info', 'Slug', 'Price', 'Status', 'PDF']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for product in Product.objects.all():
                writer.writerow({
                    'Category': product.category,
                    'Name': product.name,
                    'Balance': product.Balance,
                    'Title': product.Title,
                    'Info': product.Info,
                    'Slug': product.slug,
                    'Price': product.price,
                    'Status': product.Status,
                    'PDF': product.pdf
                })

        self.stdout.write(self.style.SUCCESS('Products exported successfully.'))