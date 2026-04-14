"""
Tests for links app.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from links.models import Link


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.mark.django_db
class TestLinkCreation:
    def test_create_short_url(self, api_client, user):
        api_client.force_authenticate(user=user)

        response = api_client.post(reverse('link-list-create'), {
            'original_url': 'https://www.example.com/very/long/url'
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert 'short_code' in response.data
        assert 'short_url' in response.data

    def test_create_with_custom_slug(self, api_client, user):
        api_client.force_authenticate(user=user)

        response = api_client.post(reverse('link-list-create'), {
            'original_url': 'https://www.example.com',
            'custom_slug': 'my-custom-link'
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_with_expiration(self, api_client, user):
        api_client.force_authenticate(user=user)

        response = api_client.post(reverse('link-list-create'), {
            'original_url': 'https://www.example.com',
            'expires_at': '2026-12-31T23:59:59Z'
        })

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestLinkRedirect:
    def test_redirect_increments_count(self, user):
        link = Link.objects.create(
            owner=user,
            original_url='https://www.example.com',
            short_code='test123'
        )

        initial_count = link.click_count

        # Simulate redirect
        from django.test import Client
        client = Client()
        client.get(f'/{link.short_code}/')

        link.refresh_from_db()
        assert link.click_count > initial_count
