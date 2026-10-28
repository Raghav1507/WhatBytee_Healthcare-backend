"""Shared pagination for all API list endpoints."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Page-number pagination with a client-adjustable page size.

    Clients may request between 1 and 100 results per page with
    ``?page_size=25``. The paginated payload is wrapped in the project's
    standard success envelope so every list endpoint returns the same shape.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "OK",
                "data": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                },
            }
        )
