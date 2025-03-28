from django.db import models
from django.urls import reverse
from django.utils.text import slugify
# Category Model
class Category(models.Model):
    location_choices = (
        ('USA', 'USA'),
        ('UK', 'UK'),
        ('Canada', 'Canada'),
        ('Other', 'Other'),
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    location = models.CharField(choices=location_choices, default='USA', max_length=255)
    class Meta:
        verbose_name_plural = 'categories'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = original_slug = slugify(self.name)
            num = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)

        
    def __str__(self):
           return self.name
#PRODUCT MODEL      
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    name = models.CharField(max_length=255,help_text="Not shown but required")
    Balance = models.CharField(max_length=255,blank=True)
    Title = models.CharField(max_length=255,blank=True)
    Info = models.TextField(blank=True)
    slug = models.SlugField(max_length=255)
    price = models.FloatField( blank=True,null=True)
    Status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    pdf = models.FileField(null=True, blank=True, upload_to='pdfs/')
    
    
    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('created',)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        # Check if the slug already exists
        if Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            # Add a unique suffix to the slug
            self.slug = f"{self.slug}-{self.pk}"
            self.save()
    
    def get_absolute_url(self):
        return reverse('front:product_detail',args=[self.slug])

    def __str__(self):
        return self.name
        