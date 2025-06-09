from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django_email_verification import urls as email_verification_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('links.urls')),
    path('accounts/', include('accounts.urls')),
    path('verify/', include(email_verification_urls)),
    path('social-auth/', include('social_django.urls', namespace='social')),
]

# Подключаем медиафайлы **только в режиме разработки**
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)