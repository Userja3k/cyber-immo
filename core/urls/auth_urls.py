from django.urls import path
from core.views.auth_views import *

app_name = 'auth'

urlpatterns = [
    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('admin-portal/', admin_portal_view, name='admin_portal'),
]