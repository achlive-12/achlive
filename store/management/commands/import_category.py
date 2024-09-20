import csv
from django.core.management.base import BaseCommand
from store.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import categories from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the input CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        categories_to_create = []

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                slug = row['slug'] if row['slug'] else slugify(name)
                location = row['location']

                categories_to_create.append(Category(
                    name=name,
                    slug=slug,
                    location=location
                ))

        Category.objects.bulk_create(categories_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Categories imported successfully.'))