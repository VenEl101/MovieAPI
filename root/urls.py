from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from root.settings import MEDIA_ROOT, MEDIA_URL, STATIC_URL, STATIC_ROOT

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/', include('app.urls')),
                path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

                path('docs/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
                path('docs/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
              ] + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)


