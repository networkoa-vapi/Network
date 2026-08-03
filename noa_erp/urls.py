"""
URL configuration for NOA ERP project.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django's built-in admin login page auto-shows a "Forgotten your login
    # credentials?" link whenever a URL named 'admin_password_reset' exists.
    # Must come before 'admin/' below, which would otherwise swallow this path.
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='portal/password_reset_form.html',
        email_template_name='portal/password_reset_email.html',
        subject_template_name='portal/password_reset_subject.txt',
        success_url='/accounts/password_reset/done/',
    ), name='admin_password_reset'),

    path('admin/', admin.site.urls),
    path('chaining/', include('smart_selects.urls')),

    # Forgot password - available from the portal login page for every user
    # (admin/staff, engineers, and customers alike).
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='portal/password_reset_form.html',
        email_template_name='portal/password_reset_email.html',
        subject_template_name='portal/password_reset_subject.txt',
        success_url='/accounts/password_reset/done/',
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='portal/password_reset_done.html',
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='portal/password_reset_confirm.html',
        success_url='/accounts/reset/done/',
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='portal/password_reset_complete.html',
    ), name='password_reset_complete'),

    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
