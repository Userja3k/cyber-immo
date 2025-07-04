from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('manager/', include('core.urls.manager_urls')),
    path('updater/', include('core.urls.updater_urls')),
    path('api/', include('core.urls.api_urls')),
    path('auth/', include('core.urls.auth_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)