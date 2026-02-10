"""
URL configuration for the music API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, InstrumentationCategoryViewSet, DataSourceViewSet,
    ComposerViewSet, WorkViewSet, TagViewSet, StatsViewSet
)
from .auth_views import login_view, logout_view, get_csrf_token, current_user
from .suggestion_views import submit_suggestion, submit_new_work_suggestion
from .admin_views import update_all_is_living

# Create router and register viewsets
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'instrumentations', InstrumentationCategoryViewSet, basename='instrumentation')
router.register(r'sources', DataSourceViewSet, basename='source')
router.register(r'composers', ComposerViewSet, basename='composer')
router.register(r'works', WorkViewSet, basename='work')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/csrf/', get_csrf_token, name='csrf'),
    path('auth/user/', current_user, name='current-user'),
    
    # Suggestion endpoints
    path('suggestions/', submit_suggestion, name='submit-suggestion'),
    path('suggestions/new-work/', submit_new_work_suggestion, name='submit-new-work-suggestion'),
    
    # Admin maintenance endpoints
    path('admin/update-is-living/', update_all_is_living, name='update-is-living'),
    
    # API endpoints
    path('', include(router.urls)),
]
