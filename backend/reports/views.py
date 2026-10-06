from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import (
    build_inventory_report,
    export_inventory_csv,
    export_inventory_excel,
    params_from_query,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def inventory_report(request):
    """
    GET|POST /api/reports/inventory

    Query / body:
      jurisdiction, topic, status,
      include_ids / exclude_ids (comma-separated or list),
      ordering, format=json|csv|xlsx
    """
    raw = {}
    raw.update(request.query_params.dict())
    if request.method == "POST" and isinstance(request.data, dict):
        raw.update(request.data)

    params = params_from_query(raw)
    report = build_inventory_report(params)
    fmt = (raw.get("format") or "json").lower()

    if fmt == "csv":
        payload = export_inventory_csv(report.rows)
        resp = HttpResponse(payload, content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = 'attachment; filename="legislative_inventory.csv"'
        return resp

    if fmt in ("xlsx", "excel"):
        payload = export_inventory_excel(report.rows)
        resp = HttpResponse(
            payload,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = 'attachment; filename="legislative_inventory.xlsx"'
        return resp

    return Response(
        {
            "total": report.total,
            "aggregates": report.aggregates,
            "filters": {
                "jurisdiction": params.jurisdiction,
                "topic": params.topic,
                "status": params.status,
                "include_ids": params.include_ids,
                "exclude_ids": params.exclude_ids,
                "ordering": params.ordering,
            },
            "results": report.rows,
        },
        status=status.HTTP_200_OK,
    )
