"""
Admin configuration for analytics app.
"""
from django.contrib import admin
from .models import ClickEvent, DailyStats


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ['link', 'clicked_at', 'ip_address', 'referer']
    list_filter = ['clicked_at', 'link']
    search_fields = ['ip_address', 'link__short_code']
    readonly_fields = ['link', 'clicked_at', 'ip_address', 'user_agent', 'referer']


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['link', 'date', 'clicks', 'unique_clicks']
    list_filter = ['date', 'link']
    search_fields = ['link__short_code']
    readonly_fields = ['link', 'date', 'clicks', 'unique_clicks']
