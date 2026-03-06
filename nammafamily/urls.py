from django.contrib import admin
from django.urls import path, include
from shop.views import home
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    # redirect default post-login profile URL to admin index to avoid 404
    path('accounts/profile/', RedirectView.as_view(url='/admin/', permanent=False)),
    # email-based password reset (development)
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
