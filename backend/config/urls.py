"""
URL configuration for URL Shortener project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from links.views import LinkRedirectView

def health_check(request):
    """Health check endpoint for monitoring."""
    return JsonResponse({'status': 'healthy', 'timestamp': __import__('datetime').datetime.now().isoformat()})

def readiness_check(request):
    """Readiness check endpoint."""
    return JsonResponse({'status': 'ready'})

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health & Monitoring
    path('health/', health_check, name='health'),
    path('ready/', readiness_check, name='ready'),
    path('metrics/', include('django_prometheus.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/links/', include('links.urls')),
    path('api/analytics/', include('analytics.urls')),

    # Redirect endpoint (must be last)
    path('<str:short_code>/', LinkRedirectView.as_view(), name='link-redirect'),
]
