from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urls = [
    path('', include('recipes.urls')),
    path('', include('users.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urls))
]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
