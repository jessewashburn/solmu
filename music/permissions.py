"""
Custom permissions for admin operations.
"""
from rest_framework import permissions


class IsHardcodedAdmin(permissions.BasePermission):
    """
    Permission check for hardcoded admin session.
    """
    
    def has_permission(self, request, view):
        return request.session.get('is_admin', False)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Read access (GET, HEAD, OPTIONS): Anyone
    - Write access (POST, PUT, PATCH, DELETE): Hardcoded admin only
    """
    
    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access requires hardcoded admin session
        return request.session.get('is_admin', False)
    
    def has_object_permission(self, request, view, obj):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write access requires hardcoded admin session
        return request.session.get('is_admin', False)
