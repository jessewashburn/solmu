from rest_framework.pagination import PageNumberPagination

class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class that allows clients to request large result sets.
    """
    page_size = 50  # Reduced for faster loading with remote DB
    page_size_query_param = 'page_size'  # Allow client to set page size via query param
    max_page_size = 1000  # Reduced max for performance
