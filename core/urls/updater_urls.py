from django.urls import path
from core.views.updater_views import *

app_name = 'updater'

urlpatterns = [
    path('', updater_dashboard, name='dashboard'),
    path('proprietes/', updater_proprietes, name='proprietes'),
    path('proprietes/<uuid:pk>/photos/', updater_photos, name='photos'),
    path('proprietes/add/', updater_add_propriete, name='add_propriete'),
    path('carte/', updater_carte, name='carte'),
    path('feed/', updater_feed, name='feed'),
    path('settings/', updater_settings, name='settings'),
    path('upload-photo/', upload_photo_ajax, name='upload_photo'),
    path('delete-photo/<int:photo_id>/', delete_photo_ajax, name='delete_photo'),
]