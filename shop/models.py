from django.db import models
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, default='')

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/', blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_shipping = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    @property
    def final_price(self):
        # use Decimal for safe arithmetic between DecimalFields and constants
        try:
            return self.original_price * (Decimal('1') - (self.discount_percent / Decimal('100')))
        except Exception:
            # fallback: coerce to Decimal strings
            op = Decimal(str(self.original_price))
            dp = Decimal(str(self.discount_percent))
            return op * (Decimal('1') - (dp / Decimal('100')))

    def __str__(self):
        return self.name

class Offer(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    banner_image = models.ImageField(upload_to='offers/', blank=True)

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def __str__(self):
        return self.title

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
    ]
    name = models.CharField(max_length=50, choices=PAYMENT_TYPES, unique=True)
    enabled = models.BooleanField(default=True)
    upi_qr_code = models.ImageField(upload_to='payments/', blank=True, null=True)
    bank_details = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()

from django.db import models

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.ForeignKey(
        'PaymentMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    items = models.JSONField()  # cart items stored as JSON

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} | {self.customer_name} | {self.status}"


class SiteSettings(models.Model):
    """Store company-wide settings editable via Django admin.

    Only one instance is expected; admin will prevent creating more than one.
    """
    company_name = models.CharField(max_length=200, default='Namma Family')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="International format without '+' e.g. 919999999999")
    google_map_embed = models.TextField(blank=True, help_text='Paste Google Maps iframe embed code or URL')

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return f"Site settings ({self.company_name})"





