"""
URL patterns for analytics app.
"""
from django.urls import path
from .views import (
    AnalyticsSummaryView, LinkAnalyticsView, ClickEventsView, 
    BulkAnalyticsView, DeviceAccessView, IPLocationListView, IPLocationStatsView
)

urlpatterns = [
    path('summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('link/<int:pk>/', LinkAnalyticsView.as_view(), name='link-analytics'),
    path('link/<int:link_id>/events/', ClickEventsView.as_view(), name='click-events'),
    path('link/<int:link_id>/devices/', DeviceAccessView.as_view(), name='device-access'),
    path('link/<int:link_id>/ip-locations/', IPLocationListView.as_view(), name='ip-locations'),
    path('link/<int:link_id>/ip-stats/', IPLocationStatsView.as_view(), name='ip-stats'),
    path('bulk/', BulkAnalyticsView.as_view(), name='bulk-analytics'),
]
