from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('faculty/', include('faculty.urls')),
    path('housing/', include('housing.urls')),
    path('plans/', include('plans.urls')),
    path('dashboard/',  include('dashboard.urls')),
    path('events/', include('events.urls')),
    path('attendance/', include('attendance.urls')),
]               

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)