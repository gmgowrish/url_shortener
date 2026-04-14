"""
Models for analytics tracking.
"""
from django.db import models
from django.conf import settings
from links.models import Link


class DeviceInfo(models.Model):
    """Track devices that accessed links."""

    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='device_accesses')
    ip_address = models.GenericIPAddressField()
    device_model = models.CharField(max_length=255, blank=True, default='Unknown')
    device_type = models.CharField(
        max_length=50, 
        choices=[
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('desktop', 'Desktop'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Geolocation fields
    country = models.CharField(max_length=100, blank=True, default='Unknown')
    country_code = models.CharField(max_length=2, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='Unknown')
    region = models.CharField(max_length=100, blank=True, default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timezone = models.CharField(max_length=50, blank=True, default='')
    isp = models.CharField(max_length=255, blank=True, default='')
    
    first_access = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(auto_now=True)
    access_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['link', 'ip_address']
        ordering = ['-last_access']
        indexes = [
            models.Index(fields=['link', '-last_access']),
            models.Index(fields=['country_code']),
        ]

    def __str__(self):
        return f'{self.device_model} ({self.ip_address}) - {self.link.short_code} - {self.country}'


class ClickEvent(models.Model):
    """Track individual click events."""

    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='click_events')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    referer = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=2, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['link', '-clicked_at']),
            models.Index(fields=['clicked_at']),
        ]

    def __str__(self):
        return f'Click on {self.link.short_code} at {self.clicked_at}'

    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['link', '-clicked_at']),
            models.Index(fields=['clicked_at']),
        ]

    def __str__(self):
        return f'Click on {self.link.short_code} at {self.clicked_at}'


class DailyStats(models.Model):
    """Aggregated daily statistics."""

    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()
    clicks = models.PositiveIntegerField(default=0)
    unique_clicks = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['link', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.link.short_code} - {self.date}: {self.clicks} clicks'
