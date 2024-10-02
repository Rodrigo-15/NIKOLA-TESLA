from django.contrib import admin
from django.urls import path, include
from reportes.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("economicos/", include("economicos.urls")),
    path("academicos/", include("academicos.urls")),
    path("accounts/", include("accounts.urls")),
    path("reportes/", include("reportes.urls")),
    path("core/", include("core.urls")),
    path("desk/", include("desk.urls")),
]

urlpatterns += static(settings.MEDIA_LOCAL_URL, document_root=settings.MEDIA_ROOT)
