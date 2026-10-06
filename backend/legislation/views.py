from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import LegislationFilter
from .models import Jurisdiction, Legislation, Status, Topic
from .serializers import LegislationSerializer


class LegislationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/legislation
    GET /api/legislation/{id}
    GET /api/legislation/meta — filter option lists
    """

    queryset = Legislation.objects.all()
    serializer_class = LegislationSerializer
    filterset_class = LegislationFilter
    search_fields = ["code", "title", "summary", "issuing_body"]
    ordering_fields = [
        "code",
        "title",
        "jurisdiction",
        "topic",
        "status",
        "effective_date",
        "last_amended",
    ]
    ordering = ["jurisdiction", "code"]

    @action(detail=False, methods=["get"], url_path="meta")
    def meta(self, request):
        return Response(
            {
                "jurisdictions": [c.value for c in Jurisdiction],
                "topics": [c.value for c in Topic],
                "statuses": [c.value for c in Status],
                "comparison_fields": [
                    "scope",
                    "enforcement_authority",
                    "penalty_max",
                    "reporting_obligation",
                    "cross_border_rules",
                    "status",
                    "effective_date",
                    "issuing_body",
                ],
            }
        )
