from django.contrib import admin
from .models import Product, Category, Offer, PaymentMethod, Order, SiteSettings
from django.utils.html import format_html
from django.db.utils import OperationalError
from django.contrib.auth.models import User, Group

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'original_price', 'discount_percent', 'final_price', 'free_shipping']
    list_filter = ['category', 'free_shipping']

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'discount_percent', 'is_active']

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'enabled']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'phone', 'total_amount', 'payment_method', 'created_at']
    readonly_fields = ['created_at']


class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'whatsapp_number', 'logo_preview', 'short_address']
    readonly_fields = ['logo_preview']
    fields = ('company_name', 'email', 'phone', 'whatsapp_number', 'logo', 'address', 'google_map_embed', 'logo_preview')

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Logo'

    def short_address(self, obj):
        if obj.address:
            return (obj.address[:50] + '...') if len(obj.address) > 50 else obj.address
        return '-'
    short_address.short_description = 'Address'

    def has_add_permission(self, request):
        # Allow adding only if no settings exist
        try:
            count = SiteSettings.objects.count()
        except OperationalError:
            # DB table missing (migrations not applied yet) — allow add so admin works
            return True

        return count == 0

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting settings to keep at least one record
        return False

# Register models
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)

# For access control, use groups: Admin, Employee
# Admin has all permissions, Employee has view/change on Order, PaymentMethod
