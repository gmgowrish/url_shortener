"""
Serializers for links app.
"""
from django.db import models
from rest_framework import serializers
from .models import Link


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for Link model."""

    short_url = serializers.SerializerMethodField()
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Link
        fields = ['id', 'original_url', 'short_code', 'short_url', 'title',
                  'description', 'custom_slug', 'is_active', 'expires_at',
                  'click_count', 'unique_clicks', 'owner_username',
                  'created_at', 'updated_at', 'last_clicked_at']
        read_only_fields = ['id', 'short_code', 'short_url', 'click_count',
                            'unique_clicks', 'owner_username', 'created_at',
                            'updated_at', 'last_clicked_at']

    def get_short_url(self, obj):
        return obj.get_short_url()

    def validate_original_url(self, value):
        """Validate the original URL."""
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        return value

    def validate_custom_slug(self, value):
        """Validate custom slug format."""
        if value:
            if not value.replace('-', '').isalnum():
                raise serializers.ValidationError(
                    'Custom slug can only contain letters, numbers, and hyphens'
                )
        return value


class LinkCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating links."""

    short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ['id', 'original_url', 'title', 'description',
                  'custom_slug', 'expires_at', 'short_code', 'short_url']
        read_only_fields = ['id', 'short_code', 'short_url']

    def get_short_url(self, obj):
        return obj.get_short_url()

    def validate_original_url(self, value):
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        return value

    def create(self, validated_data):
        short_code = Link.create_short_code()
        owner = validated_data.pop('owner', None)

        link = Link.objects.create(
            owner=owner,
            short_code=short_code,
            **validated_data
        )

        # Update user's link count
        owner.links_created = models.F('links_created') + 1
        owner.save(update_fields=['links_created'])

        return link


class LinkListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for link listing."""

    short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ['id', 'original_url', 'short_code', 'short_url', 'title',
                  'is_active', 'click_count', 'created_at', 'expires_at']
        read_only_fields = fields

    def get_short_url(self, obj):
        return obj.get_short_url()
