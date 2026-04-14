"""
URL patterns for links app.
"""
from django.urls import path
from .views import LinkListCreateView, LinkDetailView, QRCodeView

urlpatterns = [
    path('', LinkListCreateView.as_view(), name='link-list-create'),
    path('<int:pk>/', LinkDetailView.as_view(), name='link-detail'),
    path('<str:short_code>/qr/', QRCodeView.as_view(), name='link-qr'),
]
