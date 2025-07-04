from django.urls import path
from core.views.manager_views import *

app_name = 'manager'

urlpatterns = [
    path('', manager_dashboard, name='dashboard'),
    path('proprietes/', manager_proprietes, name='proprietes'),
    path('proprietes/add/', manager_add_propriete, name='add_propriete'),
    path('proprietes/<uuid:pk>/edit/', manager_edit_propriete, name='edit_propriete'),
    path('proprietes/<uuid:pk>/delete/', manager_delete_propriete, name='delete_propriete'),
    path('ventes/', manager_ventes, name='ventes'),
    path('ventes/add/', manager_add_vente, name='add_vente'),
    path('statistiques/', manager_statistiques, name='statistiques'),
    path('utilisateurs/', manager_utilisateurs, name='utilisateurs'),
    path('feed/', manager_feed, name='feed'),
    path('settings/', manager_settings, name='settings'),
    path('export/pdf/', export_pdf, name='export_pdf'),
]