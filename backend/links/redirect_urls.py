"""
URL patterns for redirect handling.
This should be included at the root level to catch short codes.
"""
from django.urls import path
from .views import LinkRedirectView

urlpatterns = [
    path('', LinkRedirectView.as_view(), name='link-redirect'),
]
