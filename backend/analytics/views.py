"""
Views for analytics app.
"""
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from links.models import Link
from .models import ClickEvent, DailyStats, DeviceInfo
from .serializers import LinkAnalyticsSerializer, AnalyticsSummarySerializer, ClickEventSerializer, DailyStatsSerializer, DeviceInfoSerializer


class LinkAnalyticsView(generics.RetrieveAPIView):
    """Get detailed analytics for a specific link."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LinkAnalyticsSerializer

    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user)


class AnalyticsSummaryView(APIView):
    """Get overall analytics summary for the user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()

        user_links = Link.objects.filter(owner=request.user)
        stats_by_date = {
            stat['date']: stat['clicks_sum'] or 0
            for stat in DailyStats.objects.filter(
                link__owner=request.user,
                date__gte=today - timedelta(days=6),
                date__lte=today,
            ).values('date').annotate(clicks_sum=Sum('clicks'))
        }

        clicks_today = stats_by_date.get(today, 0)

        # Calculate summary stats
        summary = {
            'total_links': user_links.count(),
            'total_clicks': sum(link.click_count for link in user_links),
            'total_unique_clicks': sum(link.unique_clicks for link in user_links),
            'links_created_today': user_links.filter(created_at__date=today).count(),
            'clicks_today': clicks_today,
            'top_links': [
                {
                    'short_code': link.short_code,
                    'title': link.title or link.original_url[:50],
                    'clicks': link.click_count
                }
                for link in user_links.order_by('-click_count')[:5]
            ]
        }

        # Clicks over time (last 7 days)
        clicks_over_time = []
        for i in range(7):
            date = today - timedelta(days=i)
            clicks_over_time.append({
                'date': date.isoformat(),
                'clicks': stats_by_date.get(date, 0)
            })
        summary['clicks_over_time'] = list(reversed(clicks_over_time))

        return Response(summary)


class ClickEventsView(generics.ListAPIView):
    """List click events for a specific link."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClickEventSerializer

    def get_queryset(self):
        link_id = self.kwargs.get('link_id')
        return ClickEvent.objects.filter(
            link_id=link_id,
            link__owner=self.request.user
        ).order_by('-clicked_at')[:100]


class BulkAnalyticsView(APIView):
    """Get analytics for multiple links at once."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        link_ids = request.query_params.get('ids', '').split(',')
        link_ids = [id for id in link_ids if id.isdigit()]

        links = Link.objects.filter(
            id__in=link_ids,
            owner=request.user
        )

        data = [
            {
                'id': link.id,
                'short_code': link.short_code,
                'clicks': link.click_count,
                'unique_clicks': link.unique_clicks,
                'last_clicked_at': link.last_clicked_at
            }
            for link in links
        ]

        return Response({'analytics': data})


class DeviceAccessView(generics.ListAPIView):
    """List devices that accessed a specific link."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceInfoSerializer
    pagination_class = None

    def get_queryset(self):
        link_id = self.kwargs.get('link_id')
        return DeviceInfo.objects.filter(
            link_id=link_id,
            link__owner=self.request.user
        ).order_by('-last_access')


class IPLocationListView(generics.ListAPIView):
    """
    List all device IPs with geolocation for a specific link.
    Supports filtering by country, city and IP search.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeviceInfoSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ip_address', 'country', 'city', 'isp']
    ordering_fields = ['access_count', 'last_access', 'country', 'city']
    ordering = ['-access_count']

    def get_queryset(self):
        link_id = self.kwargs.get('link_id')
        queryset = DeviceInfo.objects.filter(
            link_id=link_id,
            link__owner=self.request.user
        )

        # Filter by country code if provided
        country_code = self.request.query_params.get('country_code')
        if country_code:
            queryset = queryset.filter(country_code__iexact=country_code)

        # Filter by city if provided
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        # Filter by device type if provided
        device_type = self.request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)

        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(last_access__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(last_access__date__lte=date_to)

        return queryset.order_by('-access_count')


class IPLocationStatsView(APIView):
    """
    Get aggregated statistics about IP locations for a link.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, link_id):
        # Verify user owns the link
        link = Link.objects.filter(id=link_id, owner=request.user).first()
        if not link:
            return Response({'error': 'Link not found'}, status=404)

        devices = DeviceInfo.objects.filter(link=link)

        # Country statistics
        country_stats = devices.values('country_code', 'country').annotate(
            count=Count('id'),
            total_accesses=Sum('access_count')
        ).order_by('-total_accesses')

        # City statistics
        city_stats = devices.values('city', 'country').annotate(
            count=Count('id'),
            total_accesses=Sum('access_count')
        ).order_by('-total_accesses')[:20]

        # Device type statistics
        device_stats = devices.values('device_type').annotate(
            count=Count('id'),
            total_accesses=Sum('access_count')
        )

        # Total unique IPs
        total_unique_ips = devices.count()
        total_accesses = devices.aggregate(Sum('access_count'))['access_count__sum'] or 0

        return Response({
            'total_unique_ips': total_unique_ips,
            'total_accesses': total_accesses,
            'countries': list(country_stats),
            'cities': list(city_stats),
            'device_types': list(device_stats),
        })
