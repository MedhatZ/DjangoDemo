from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import DEFAULT_COMPARE_FIELDS, ComparisonConfig
from .serializers import ComparisonConfigSerializer
from .services import (
    build_comparison_matrix,
    export_comparison_excel,
    resolve_records,
)


class ComparisonConfigViewSet(viewsets.ModelViewSet):
    """
    CRUD for saved comparison configs.
    GET/POST   /api/comparisons
    GET/PATCH/DELETE /api/comparisons/{id}
    POST /api/comparisons/preview — build matrix without saving
    POST /api/comparisons/{id}/export — Excel export of saved config
    """

    serializer_class = ComparisonConfigSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return ComparisonConfig.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="preview")
    def preview(self, request):
        jurisdictions = request.data.get("jurisdictions") or []
        topic = request.data.get("topic") or None
        fields = request.data.get("fields") or list(DEFAULT_COMPARE_FIELDS)
        legislation_ids = request.data.get("legislation_ids") or []

        if len(jurisdictions) < 1 and not legislation_ids:
            return Response(
                {"detail": "Provide jurisdictions or legislation_ids."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records = resolve_records(
            jurisdictions=jurisdictions,
            topic=topic,
            legislation_ids=legislation_ids or None,
        )
        matrix = build_comparison_matrix(records, fields)

        fmt = (request.data.get("format") or "json").lower()
        if fmt in ("xlsx", "excel"):
            payload = export_comparison_excel(matrix)
            resp = HttpResponse(
                payload,
                content_type=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
            resp["Content-Disposition"] = (
                'attachment; filename="regulatory_comparison.xlsx"'
            )
            return resp

        return Response(matrix)

    @action(detail=True, methods=["get", "post"], url_path="run")
    def run(self, request, pk=None):
        config = self.get_object()
        records = resolve_records(
            jurisdictions=config.jurisdictions,
            topic=config.topic or None,
            legislation_ids=config.legislation_ids or None,
        )
        matrix = build_comparison_matrix(records, config.fields or None)
        return Response({"config": ComparisonConfigSerializer(config).data, **matrix})

    @action(detail=True, methods=["get"], url_path="export")
    def export(self, request, pk=None):
        config = self.get_object()
        records = resolve_records(
            jurisdictions=config.jurisdictions,
            topic=config.topic or None,
            legislation_ids=config.legislation_ids or None,
        )
        matrix = build_comparison_matrix(records, config.fields or None)
        payload = export_comparison_excel(matrix)
        resp = HttpResponse(
            payload,
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in config.name)
        resp["Content-Disposition"] = (
            f'attachment; filename="comparison_{safe_name or "export"}.xlsx"'
        )
        return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def comparison_field_catalog(request):
    return Response({"fields": DEFAULT_COMPARE_FIELDS})
