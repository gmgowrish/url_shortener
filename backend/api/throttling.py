"""
Custom throttling classes for rate limiting.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LinkCreateThrottle(UserRateThrottle):
    """Rate limit for link creation."""

    scope = 'link_create'
    rate = '20/hour'


class BurstRateThrottle(AnonRateThrottle):
    """Prevent burst requests from anonymous users."""

    rate = '10/minute'


class SustainedRateThrottle(AnonRateThrottle):
    """Sustained rate limit for anonymous users."""

    rate = '100/hour'
