from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Класс кастомного пагинатора"""

    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
