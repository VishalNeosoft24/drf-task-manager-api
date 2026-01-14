from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

class UserPagination(PageNumberPagination):
    page_size = 18
    page_size_query_param = 'page_size'
    max_page_size = 50

def paginate_queryset(request, queryset, serializer_class, pagination_class, message=None):
    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = serializer_class(page, many=True)     
        return Response({
            "message": message,
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }, status=status.HTTP_200_OK)
