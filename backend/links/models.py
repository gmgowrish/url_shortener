"""
Models for URL shortening functionality.
"""
import random
import string
from django.db import models
from django.conf import settings


def generate_short_code(length=None):
    """Generate a random short code."""
    if length is None:
        length = settings.SHORT_CODE_LENGTH

    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


class Link(models.Model):
    """Model representing a shortened URL."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='links'
    )
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')

    # Metadata
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    custom_slug = models.CharField(max_length=50, blank=True, unique=True, null=True)

    # Tracking
    click_count = models.PositiveIntegerField(default=0)
    unique_clicks = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['owner', '-created_at']),
        ]

    def __str__(self):
        return f'{self.short_code} -> {self.original_url[:50]}'

    def get_short_url(self):
        """Get the full shortened URL."""
        from django.conf import settings
        return f'{settings.BASE_URL}/{self.short_code}'

    def is_expired(self):
        """Check if the link has expired."""
        if self.expires_at is None:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def increment_click_count(self):
        """Increment click counter."""
        self.click_count = models.F('click_count') + 1
        self.save(update_fields=['click_count'])
        # Refresh to get actual value
        self.refresh_from_db()

    @classmethod
    def create_short_code(cls, length=None):
        """Create a unique short code."""
        while True:
            code = generate_short_code(length)
            if not cls.objects.filter(short_code=code).exists():
                return code
