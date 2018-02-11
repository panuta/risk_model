from django.urls import path

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include('app.risk.urls', namespace='risk')),
    path('api/', include('app.risk.api.urls', namespace='risk_api')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
