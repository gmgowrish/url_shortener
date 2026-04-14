"""
Custom permissions.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsActiveUser(permissions.BasePermission):
    """
    Permission to only allow active users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_active
