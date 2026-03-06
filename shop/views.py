from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages

from .models import Product, Category, Offer, PaymentMethod, Order
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse
from .models import SiteSettings
from django.db.utils import OperationalError


# =========================
# HOME PAGE
# =========================
def home(request):
    # read filters
    category_id = request.GET.get('category')
    q = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()
    categories = Category.objects.all()

    # category may come as id (from template) or slug; handle both
    if category_id:
        # try numeric id first
        try:
            products = products.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            products = products.filter(category__slug=category_id)

    if q:
        products = products.filter(name__icontains=q) | products.filter(description__icontains=q)

    try:
        if min_price:
            products = products.filter(original_price__gte=float(min_price))
        if max_price:
            products = products.filter(original_price__lte=float(max_price))
    except ValueError:
        # ignore invalid numeric filters
        pass

    offers = Offer.objects.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )

    try:
        site = SiteSettings.objects.first()
    except OperationalError:
        site = None
    context = {
        'products': products,
        'categories': categories,
        'offers': offers,
        'now': timezone.now(),
    }

    if site:
        context.update({
            'company_name': site.company_name,
            'company_email': site.email,
            'company_phone': site.phone,
            'company_address': site.address,
            'whatsapp_number': site.whatsapp_number,
            'company_logo_url': site.logo.url if site.logo else None,
            'google_map_embed': site.google_map_embed,
        })
    else:
        context.update({
            'company_name': getattr(settings, 'COMPANY_NAME', 'Company'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', ''),
            'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
            'company_address': getattr(settings, 'COMPANY_ADDRESS', ''),
            'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', ''),
            'company_logo_url': None,
            'google_map_embed': '',
        })

    return render(request, 'shop/home.html', context)


# =========================
# PRODUCT DETAIL
# =========================
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {
        'product': product
    })


# =========================
# ADD TO CART
# =========================
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    return redirect('cart')


def admin_forgot_password(request):
    """A simple password-reset-by-secret view for admins.

    WARNING: This exposes a reset endpoint protected only by a shared secret
    string from settings. Set a strong value in settings.ADMIN_PASSWORD_RESET_KEY
    before enabling. This view will set the given user's password immediately.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        secret = request.POST.get('secret')

        key = getattr(settings, 'ADMIN_PASSWORD_RESET_KEY', None)
        if not key:
            return HttpResponse('Password reset is not configured on this site.', status=403)

        if secret != key:
            return HttpResponse('Invalid secret key.', status=403)

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse('User not found.', status=404)

        user.set_password(new_password)
        user.save()

        # redirect to admin login
        return redirect('/admin/login/')

    return render(request, 'shop/admin_forgot_password.html', {})


# =========================
# CART PAGE (IMAGE FIX HERE)
# =========================
def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))

        item_total = product.final_price * quantity
        if not product.free_shipping:
            item_total += product.shipping_price * quantity

        items.append({
            'product': product,          # 🔹 FULL PRODUCT OBJECT
            'product_image': product.image.url if product.image else None,
            'quantity': quantity,
            'total': item_total
        })

        total += item_total

    # build a simple WhatsApp friendly message (plain text; template will urlencode)
    lines = []
    for it in items:
        p = it['product']
        qty = it['quantity']
        unit = p.final_price
        item_total = it['total']
        # absolute URLs for product and image (if available)
        try:
            product_url = request.build_absolute_uri(p.get_absolute_url() if hasattr(p, 'get_absolute_url') else request.path)
        except Exception:
            product_url = request.build_absolute_uri(request.path)
        image_url = None
        if p.image:
            try:
                image_url = request.build_absolute_uri(p.image.url)
            except Exception:
                image_url = p.image.url

        lines.append(f"Product: {p.name}")
        lines.append(f"Quantity: {qty}")
        lines.append(f"Unit price: ₹{unit}")
        lines.append(f"Item total: ₹{item_total}")
        if image_url:
            lines.append(f"Image: {image_url}")
        lines.append(f"Product page: {product_url}")
        lines.append('')

    lines.append(f"Total: ₹{total}")
    whatsapp_message = "Order from " + context.get('company_name', 'our store') if 'context' in locals() else "Order from Namma Family"
    whatsapp_message += "\n\n" + "\n".join(lines)

    try:
        site = SiteSettings.objects.first()
    except OperationalError:
        site = None
    context = {
        'items': items,
        'total': total,
        'whatsapp_message': whatsapp_message,
        'now': timezone.now(),
    }
    if site:
        context.update({
            'company_name': site.company_name,
            'company_email': site.email,
            'company_phone': site.phone,
            'company_address': site.address,
            'whatsapp_number': site.whatsapp_number,
            'company_logo_url': site.logo.url if site.logo else None,
            'google_map_embed': site.google_map_embed,
        })
    else:
        context.update({
            'company_name': getattr(settings, 'COMPANY_NAME', 'Company'),
            'company_email': getattr(settings, 'COMPANY_EMAIL', ''),
            'company_phone': getattr(settings, 'COMPANY_PHONE', ''),
            'company_address': getattr(settings, 'COMPANY_ADDRESS', ''),
            'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', ''),
            'company_logo_url': None,
            'google_map_embed': '',
        })

    return render(request, 'shop/cart.html', context)


# =========================
# REMOVE FROM CART
# =========================
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return redirect('cart')


def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        if quantity > 0:
            cart[str(product_id)] = quantity
        else:
            cart.pop(str(product_id), None)

        request.session['cart'] = cart

    return redirect('cart')


# =========================
# CHECKOUT (IMAGE FIX HERE)
# =========================
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))

        item_total = product.final_price * quantity
        if not product.free_shipping:
            item_total += product.shipping_price * quantity

        items.append({
            'product': product,      # ✅ IMAGE AVAILABLE
            'quantity': quantity,
            'total': item_total
        })

        total += item_total

    payment_methods = PaymentMethod.objects.filter(enabled=True)

    if request.method == 'POST':
        order = Order.objects.create(
            customer_name=request.POST.get('customer_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            total_amount=total,
            payment_method_id=request.POST.get('payment_method'),
            items=cart
        )

        request.session['cart'] = {}
        messages.success(request, 'Order placed successfully!')

        return redirect('order_success', order_id=order.id)

    return render(request, 'shop/checkout.html', {
        'items': items,
        'total': total,
        'payment_methods': payment_methods
    })


# =========================
# ORDER SUCCESS (IMAGE FIX HERE)
# =========================
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    items = []
    for product_id, quantity in order.items.items():
        product = get_object_or_404(Product, id=int(product_id))

        items.append({
            'product': product,   # ✅ IMAGE AVAILABLE
            'quantity': quantity
        })

    return render(request, 'shop/order_success.html', {
        'order': order,
        'items': items
    })
