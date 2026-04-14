"""
Admin configuration for links app.
"""
from django.contrib import admin
from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'original_url', 'owner', 'click_count',
                    'is_active', 'created_at', 'last_clicked_at']
    list_filter = ['is_active', 'created_at', 'owner']
    search_fields = ['short_code', 'original_url', 'title', 'owner__username']
    readonly_fields = ['short_code', 'click_count', 'unique_clicks', 'get_short_url']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('URL Information', {
            'fields': ('owner', 'original_url', 'short_code', 'get_short_url')
        }),
        ('Optional Fields', {
            'fields': ('title', 'description', 'custom_slug')
        }),
        ('Settings', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Statistics', {
            'fields': ('click_count', 'unique_clicks', 'last_clicked_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['deactivate_links', 'activate_links']

    def deactivate_links(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_links.short_description = 'Deactivate selected links'

    def activate_links(self, request, queryset):
        queryset.update(is_active=True)
    activate_links.short_description = 'Activate selected links'
