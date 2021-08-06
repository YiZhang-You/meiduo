from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """自定义分页"""
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 5
