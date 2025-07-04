from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views.api_views import *

router = DefaultRouter()
router.register(r'proprietes', ProprieteViewSet)
router.register(r'ventes', VenteViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', api_login, name='api_login'),
    path('auth/register/', api_register, name='api_register'),
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
]