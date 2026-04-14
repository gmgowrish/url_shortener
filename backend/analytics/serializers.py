"""
Serializers for analytics app.
"""
from rest_framework import serializers
from .models import ClickEvent, DailyStats, DeviceInfo
from links.models import Link


class DeviceInfoSerializer(serializers.ModelSerializer):
    """Serializer for device information."""

    class Meta:
        model = DeviceInfo
        fields = ['id', 'ip_address', 'device_model', 'device_type',
                  'first_access', 'last_access', 'access_count',
                  'country', 'country_code', 'city', 'region',
                  'latitude', 'longitude', 'timezone', 'isp']
        read_only_fields = fields


class ClickEventSerializer(serializers.ModelSerializer):
    """Serializer for click events."""

    class Meta:
        model = ClickEvent
        fields = ['id', 'clicked_at', 'ip_address', 'user_agent',
                  'referer', 'country', 'city']
        read_only_fields = fields


class DailyStatsSerializer(serializers.ModelSerializer):
    """Serializer for daily statistics."""

    class Meta:
        model = DailyStats
        fields = ['date', 'clicks', 'unique_clicks']
        read_only_fields = fields


class LinkAnalyticsSerializer(serializers.ModelSerializer):
    """Analytics summary for a link."""

    total_clicks = serializers.IntegerField(source='click_count')
    unique_clicks = serializers.IntegerField(read_only=True)
    recent_clicks = serializers.SerializerMethodField()
    daily_stats = serializers.SerializerMethodField()

    def get_recent_clicks(self, obj):
        events = obj.click_events.order_by('-clicked_at')[:10]
        return ClickEventSerializer(events, many=True).data

    def get_daily_stats(self, obj):
        stats = obj.daily_stats.order_by('-date')[:30]
        return DailyStatsSerializer(stats, many=True).data

    class Meta:
        model = Link
        fields = ['id', 'short_code', 'original_url', 'title', 'total_clicks',
                  'unique_clicks', 'created_at', 'last_clicked_at',
                  'recent_clicks', 'daily_stats']
        read_only_fields = fields


class AnalyticsSummarySerializer(serializers.Serializer):
    """Overall analytics summary."""

    total_links = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    total_unique_clicks = serializers.IntegerField()
    links_created_today = serializers.IntegerField()
    clicks_today = serializers.IntegerField()
    top_links = serializers.ListField()
