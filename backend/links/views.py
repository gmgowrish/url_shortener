"""
Views for links app.
"""
from rest_framework import status, generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.db import models
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import NotFound

from .models import Link
from .serializers import LinkSerializer, LinkCreateSerializer, LinkListSerializer
from analytics.models import ClickEvent, DailyStats, DeviceInfo
from analytics.geolocation import get_ip_geolocation


class LinkListCreateView(generics.ListCreateAPIView):
    """List and create links."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['original_url', 'title', 'short_code']
    ordering_fields = ['created_at', 'click_count', 'last_clicked_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LinkCreateSerializer
        return LinkListSerializer

    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific link."""

    permission_classes = [IsAuthenticated]
    serializer_class = LinkSerializer

    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user)


class LinkRedirectView(APIView):
    """Handle URL redirection with analytics."""

    permission_classes = [AllowAny]

    def get(self, request, short_code):
        # Check cache first
        cache_key = f'link:{short_code}'
        cached_link = cache.get(cache_key)

        if cached_link:
            link_id = cached_link
            link = Link.objects.get(id=link_id)
        else:
            link = get_object_or_404(Link, short_code=short_code)
            cache.set(cache_key, link.id, timeout=settings.ANALYTICS_CACHE_TIMEOUT)

        # Check if link is active
        if not link.is_active:
            raise NotFound('This link has been deactivated')

        # Check expiration
        if link.is_expired():
            raise NotFound('This link has expired')

        # Update analytics (synchronous for free tier)
        self._track_click(link, request)

        # Perform HTTP redirect
        return HttpResponseRedirect(redirect_to=link.original_url)

    def _track_click(self, link, request):
        """Track click analytics."""
        link.click_count = models.F('click_count') + 1
        link.last_clicked_at = timezone.now()

        # Simple unique click detection (by IP)
        ip = self._get_client_ip(request)
        cache_key = f'click:{link.id}:{ip}'
        is_unique_click = not cache.get(cache_key)

        if is_unique_click:
            link.unique_clicks = models.F('unique_clicks') + 1
            cache.set(cache_key, 'clicked', timeout=3600)  # 1 hour

        link.save(update_fields=['click_count', 'unique_clicks', 'last_clicked_at'])

        # Update owner's total clicks
        link.owner.total_clicks = models.F('total_clicks') + 1
        link.owner.save(update_fields=['total_clicks'])

        geo_data = get_ip_geolocation(ip) if ip != 'unknown' else None

        # Track per-click analytics and daily aggregates
        self._track_click_event(link, request, ip, geo_data, is_unique_click)

        # Track device information
        self._track_device(link, request, ip, geo_data)

    def _track_click_event(self, link, request, ip, geo_data, is_unique_click):
        """Persist click event details and update daily aggregates."""
        ClickEvent.objects.create(
            link=link,
            ip_address=None if ip == 'unknown' else ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            referer=request.META.get('HTTP_REFERER'),
            country=(geo_data or {}).get('country_code', ''),
            city=(geo_data or {}).get('city', 'Unknown'),
        )

        daily_stats, _ = DailyStats.objects.get_or_create(
            link=link,
            date=timezone.now().date(),
            defaults={'clicks': 0, 'unique_clicks': 0},
        )

        daily_stats.clicks = models.F('clicks') + 1
        update_fields = ['clicks']

        if is_unique_click:
            daily_stats.unique_clicks = models.F('unique_clicks') + 1
            update_fields.append('unique_clicks')

        daily_stats.save(update_fields=update_fields)

    def _track_device(self, link, request, ip, geo_data=None):
        """Track device information."""
        if ip == 'unknown':
            return

        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        device_type, device_model = self._parse_user_agent(user_agent)

        device_info, created = DeviceInfo.objects.get_or_create(
            link=link,
            ip_address=ip,
            defaults={
                'device_model': device_model,
                'device_type': device_type,
                'user_agent': user_agent,
            }
        )

        # Get geolocation data for the IP
        if created or not device_info.country or device_info.country == 'Unknown':
            if geo_data:
                device_info.country = geo_data.get('country', 'Unknown')
                device_info.country_code = geo_data.get('country_code', '')
                device_info.city = geo_data.get('city', 'Unknown')
                device_info.region = geo_data.get('region', '')
                device_info.latitude = geo_data.get('latitude')
                device_info.longitude = geo_data.get('longitude')
                device_info.timezone = geo_data.get('timezone', '')
                device_info.isp = geo_data.get('isp', '')

        if not created:
            device_info.access_count = models.F('access_count') + 1
            device_info.last_access = timezone.now()
            device_info.save(update_fields=['access_count', 'last_access'])
        else:
            device_info.save()

    def _parse_user_agent(self, user_agent):
        """Parse user agent to extract device type and model."""
        if not user_agent:
            return 'unknown', 'Unknown Device'

        ua_lower = user_agent.lower()

        # Detect device type
        if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower or 'ipod' in ua_lower:
            device_type = 'mobile'
        elif 'ipad' in ua_lower or 'tablet' in ua_lower or 'playbook' in ua_lower or 'nexus 7' in ua_lower or 'nexus 10' in ua_lower:
            device_type = 'tablet'
        else:
            device_type = 'desktop'

        # Extract device model
        device_model = 'Unknown Device'

        if 'iphone' in ua_lower:
            if 'iphone 15' in ua_lower:
                device_model = 'iPhone 15'
            elif 'iphone 14' in ua_lower:
                device_model = 'iPhone 14'
            elif 'iphone 13' in ua_lower:
                device_model = 'iPhone 13'
            elif 'iphone 12' in ua_lower:
                device_model = 'iPhone 12'
            else:
                device_model = 'iPhone'
        elif 'ipad' in ua_lower:
            device_model = 'iPad'
        elif 'android' in ua_lower:
            # Extract Android device model
            import re
            match = re.search(r'Android [0-9.]+; ([^;]+)', user_agent)
            if match:
                device_model = f'Android - {match.group(1)}'
            else:
                device_model = 'Android Device'
        elif 'mac' in ua_lower:
            device_model = 'MacOS'
        elif 'windows' in ua_lower:
            device_model = 'Windows'
        elif 'linux' in ua_lower:
            device_model = 'Linux'

        return device_type, device_model

    def _get_client_ip(self, request):
        """Get real client IP address from various headers."""
        # Check X-Forwarded-For first (proxy/load balancer)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP (client IP before any proxies)
            return x_forwarded_for.split(',')[0].strip()
        
        # Check CF-Connecting-IP (Cloudflare)
        cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
        if cf_ip:
            return cf_ip.strip()
        
        # Check X-Real-IP (Nginx)
        real_ip = request.META.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to REMOTE_ADDR
        remote_addr = request.META.get('REMOTE_ADDR', 'unknown')
        return remote_addr.strip() if remote_addr != 'unknown' else 'unknown'


class QRCodeView(APIView):
    """Generate QR code for a link."""

    permission_classes = [AllowAny]

    def get(self, request, short_code):
        import segno
        from django.http import HttpResponse

        link = get_object_or_404(Link, short_code=short_code)
        qr = segno.make(link.get_short_url())

        response = HttpResponse(content_type='image/svg+xml')
        qr.save(out=response, kind='svg')
        return response
