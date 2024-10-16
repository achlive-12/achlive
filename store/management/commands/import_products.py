# myapp/management/commands/import_products.py

from django.core.management.base import BaseCommand
from store.models import Category, Product
import csv
import random
from django.core.files import File
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import products from a data file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the data file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        products_to_create = []

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category_name = row['Category']
                slug = slugify(f"{row['Name']}-{random.randint(1, 1000000)}")
                category, _ = Category.objects.get_or_create(name=category_name)

                product_data = {
                    'name': row['Name'],
                    'category': category,
                    'Balance': row['Balance'],
                    'Title': row['Name'],
                    'Info': row['Info'],
                    'price': float(row['Price']),
                    'slug': slug,
                }

                pdf_path = row.get('pdf')
                if pdf_path:
                    try:
                        with open(pdf_path, 'rb') as pdf_file:
                            product_data['pdf'] = File(pdf_file)
                    except FileNotFoundError:
                        self.stdout.write(self.style.WARNING(f"PDF file not found: {pdf_path}"))

                products_to_create.append(Product(**product_data))

        Product.objects.bulk_create(products_to_create)
        self.stdout.write(self.style.SUCCESS('Products imported successfully.'))