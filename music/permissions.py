"""
Custom permissions for admin operations.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Read access (GET, HEAD, OPTIONS): Anyone
    - Write access (POST, PUT, PATCH, DELETE): Admin users only
    """
    
    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access requires authentication and staff status
        return request.user and request.user.is_authenticated and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access requires authentication and staff status
        return request.user and request.user.is_authenticated and request.user.is_staff
