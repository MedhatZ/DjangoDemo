"""
Inventory reporting logic — filter, aggregate, include/exclude, export.
Kept pure where possible so unit tests do not need HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO, StringIO
from typing import Iterable, Sequence

from django.db.models import Count, QuerySet

from legislation.models import Legislation

INVENTORY_COLUMNS = [
    "id",
    "code",
    "title",
    "jurisdiction",
    "topic",
    "status",
    "effective_date",
    "last_amended",
    "issuing_body",
    "scope",
    "enforcement_authority",
    "penalty_max",
    "reporting_obligation",
    "cross_border_rules",
]


@dataclass
class InventoryFilterParams:
    jurisdiction: str | None = None
    topic: str | None = None
    status: str | None = None
    include_ids: Sequence[int] | None = None
    exclude_ids: Sequence[int] | None = None
    ordering: str | None = None


@dataclass
class InventoryReport:
    rows: list[dict] = field(default_factory=list)
    total: int = 0
    aggregates: dict = field(default_factory=dict)


def _parse_id_list(value) -> list[int] | None:
    if value is None or value == "":
        return None
    if isinstance(value, (list, tuple)):
        return [int(x) for x in value]
    return [int(x.strip()) for x in str(value).split(",") if x.strip()]


def params_from_query(query: dict) -> InventoryFilterParams:
    return InventoryFilterParams(
        jurisdiction=query.get("jurisdiction") or None,
        topic=query.get("topic") or None,
        status=query.get("status") or None,
        include_ids=_parse_id_list(query.get("include_ids") or query.get("id__in")),
        exclude_ids=_parse_id_list(query.get("exclude_ids") or query.get("id__notin")),
        ordering=query.get("ordering") or query.get("sort") or None,
    )


def apply_inventory_filters(qs: QuerySet, params: InventoryFilterParams) -> QuerySet:
    if params.jurisdiction:
        qs = qs.filter(jurisdiction__iexact=params.jurisdiction)
    if params.topic:
        qs = qs.filter(topic__iexact=params.topic)
    if params.status:
        qs = qs.filter(status__iexact=params.status)
    if params.include_ids:
        qs = qs.filter(id__in=params.include_ids)
    if params.exclude_ids:
        qs = qs.exclude(id__in=params.exclude_ids)
    if params.ordering:
        # Support comma-separated Django ordering, e.g. "-status,jurisdiction"
        fields = [f.strip() for f in params.ordering.split(",") if f.strip()]
        if fields:
            qs = qs.order_by(*fields)
    return qs


def build_aggregates(qs: QuerySet) -> dict:
    by_jurisdiction = {
        row["jurisdiction"]: row["c"]
        for row in qs.values("jurisdiction").annotate(c=Count("id")).order_by()
    }
    by_topic = {
        row["topic"]: row["c"]
        for row in qs.values("topic").annotate(c=Count("id")).order_by()
    }
    by_status = {
        row["status"]: row["c"]
        for row in qs.values("status").annotate(c=Count("id")).order_by()
    }
    return {
        "by_jurisdiction": by_jurisdiction,
        "by_topic": by_topic,
        "by_status": by_status,
        "total": qs.count(),
    }


def serialize_row(obj: Legislation) -> dict:
    return {
        "id": obj.id,
        "code": obj.code,
        "title": obj.title,
        "jurisdiction": obj.jurisdiction,
        "topic": obj.topic,
        "status": obj.status,
        "effective_date": obj.effective_date.isoformat() if obj.effective_date else None,
        "last_amended": obj.last_amended.isoformat() if obj.last_amended else None,
        "issuing_body": obj.issuing_body,
        "scope": obj.scope,
        "enforcement_authority": obj.enforcement_authority,
        "penalty_max": obj.penalty_max,
        "reporting_obligation": obj.reporting_obligation,
        "cross_border_rules": obj.cross_border_rules,
        "summary": obj.summary,
    }


def build_inventory_report(
    params: InventoryFilterParams,
    *,
    queryset: QuerySet | None = None,
) -> InventoryReport:
    qs = queryset if queryset is not None else Legislation.objects.all()
    qs = apply_inventory_filters(qs, params)
    aggregates = build_aggregates(qs)
    rows = [serialize_row(obj) for obj in qs]
    return InventoryReport(rows=rows, total=len(rows), aggregates=aggregates)


def export_inventory_csv(rows: Iterable[dict]) -> bytes:
    import csv

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=INVENTORY_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in INVENTORY_COLUMNS})
    return buffer.getvalue().encode("utf-8-sig")


def export_inventory_excel(rows: Iterable[dict]) -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Legislative Inventory"
    ws.append(INVENTORY_COLUMNS)
    for row in rows:
        ws.append([row.get(col, "") for col in INVENTORY_COLUMNS])
    out = BytesIO()
    wb.save(out)
    return out.getvalue()
