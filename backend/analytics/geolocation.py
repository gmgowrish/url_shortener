"""
Geolocation utility for getting IP address information.
"""
import ipaddress
import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def get_ip_geolocation(ip_address):
    """
    Get geolocation information for an IP address using ip-api.com (free service).
    
    Args:
        ip_address: The IP address to lookup
        
    Returns:
        Dictionary with geolocation data or None if lookup fails
    """
    # Check cache first
    cache_key = f'geolocation_{ip_address}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        parsed_ip = ipaddress.ip_address(ip_address)
        if (
            parsed_ip.is_private
            or parsed_ip.is_loopback
            or parsed_ip.is_reserved
            or parsed_ip.is_unspecified
            or parsed_ip.is_multicast
        ):
            return None
    except ValueError:
        logger.warning(f'Invalid IP address for geolocation lookup: {ip_address}')
        return None
    
    try:
        # Using ip-api.com free service (no API key required)
        # Limit: 45 requests per minute
        response = requests.get(
            f'http://ip-api.com/json/{ip_address}',
            params={'fields': 'status,country,countryCode,city,region,lat,lon,timezone,isp'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                geolocation = {
                    'country': data.get('country', 'Unknown'),
                    'country_code': data.get('countryCode', ''),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', ''),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'timezone': data.get('timezone', ''),
                    'isp': data.get('isp', ''),
                }
                
                # Cache for 30 days
                cache.set(cache_key, geolocation, 30 * 24 * 60 * 60)
                return geolocation
        
        logger.warning(f'Failed to get geolocation for {ip_address}: {response.status_code}')
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f'Geolocation request failed for {ip_address}: {str(e)}')
        return None
    except Exception as e:
        logger.error(f'Error getting geolocation for {ip_address}: {str(e)}')
        return None


def get_ip_info_simple(ip_address):
    """
    Lightweight geolocation for storing in database.
    Uses cache to avoid repeated lookups.
    """
    return get_ip_geolocation(ip_address)
