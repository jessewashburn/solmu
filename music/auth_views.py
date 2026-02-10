"""
Authentication views for admin users.
"""
import os
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user with admin credentials from environment variables.
    
    POST /api/auth/login/
    Body: {"username": "admin", "password": "your-password"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check hardcoded credentials
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create a session marker for hardcoded auth
        request.session['is_admin'] = True
        request.session['admin_username'] = ADMIN_USERNAME
        
        return Response({
            'message': 'Login successful',
            'user': {
                'username': ADMIN_USERNAME,
                'is_staff': True,
                'is_admin': True,
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Logout current user and destroy session.
    
    POST /api/auth/logout/
    """
    request.session.flush()
    return Response({'message': 'Logout successful'})


@api_view(['GET'])
@ensure_csrf_cookie
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Get CSRF token for session authentication.
    This endpoint sets the CSRF cookie which React can read.
    
    GET /api/auth/csrf/
    """
    return Response({'message': 'CSRF cookie set'})


@api_view(['GET'])
@permission_classes([AllowAny])
def current_user(request):
    """
    Get current authenticated user info.
    
    GET /api/auth/user/
    """
    if request.session.get('is_admin'):
        return Response({
            'username': request.session.get('admin_username', 'admin'),
            'is_staff': True,
            'is_admin': True,
        })
    else:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
