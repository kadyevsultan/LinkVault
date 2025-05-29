from django.urls import path

from .views import (
    register_view, login_view, logout_view, 
    confirm_email_for_reset_password_view, 
    profile_view, delete_profile_view
)

app_name = 'accounts'

urlpatterns = [
    path('register', register_view, name='register'),
    path('login', login_view, name='login'),
    path('profile', profile_view, name='profile'),
    path('logout', logout_view, name='logout'),
    path('confirm-email-for-reset-password', confirm_email_for_reset_password_view, name='reset-password'),
    path('delete-profile', delete_profile_view, name='delete-profile'),
]
