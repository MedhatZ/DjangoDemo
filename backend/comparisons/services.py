"""
Regulatory comparison matrix builder — side-by-side structured fields.
"""
from __future__ import annotations

from io import BytesIO
from typing import Sequence

from django.db.models import QuerySet

from legislation.models import Legislation

from .models import DEFAULT_COMPARE_FIELDS


_STATUS_RANK = {"Active": 0, "Proposed": 1, "Repealed": 2}


def resolve_records(
    *,
    jurisdictions: Sequence[str],
    topic: str | None = None,
    legislation_ids: Sequence[int] | None = None,
    queryset: QuerySet | None = None,
    one_per_jurisdiction: bool = True,
) -> list[Legislation]:
    """
    Resolve legislation rows for the comparison matrix.

    When building from jurisdictions (+ optional topic), default to one
    representative record per jurisdiction (Active > Proposed > Repealed)
    so the side-by-side matrix stays readable in the demo.
    """
    qs = queryset if queryset is not None else Legislation.objects.all()
    if legislation_ids:
        return list(qs.filter(id__in=list(legislation_ids)).order_by("jurisdiction", "code"))

    if jurisdictions:
        qs = qs.filter(jurisdiction__in=list(jurisdictions))
    if topic:
        qs = qs.filter(topic__iexact=topic)
    records = list(qs.order_by("jurisdiction", "topic", "code"))

    if not one_per_jurisdiction or not jurisdictions:
        return records

    best: dict[str, Legislation] = {}
    for r in records:
        current = best.get(r.jurisdiction)
        if current is None:
            best[r.jurisdiction] = r
            continue
        if _STATUS_RANK.get(r.status, 9) < _STATUS_RANK.get(current.status, 9):
            best[r.jurisdiction] = r

    # Preserve the caller's jurisdiction order
    ordered = []
    for j in jurisdictions:
        if j in best:
            ordered.append(best[j])
    return ordered


def build_comparison_matrix(
    records: Sequence[Legislation],
    fields: Sequence[str] | None = None,
) -> dict:
    fields = list(fields) if fields else list(DEFAULT_COMPARE_FIELDS)
    columns = [
        {
            "id": r.id,
            "code": r.code,
            "title": r.title,
            "jurisdiction": r.jurisdiction,
            "topic": r.topic,
            "status": r.status,
        }
        for r in records
    ]
    matrix = []
    for field_name in fields:
        cells = []
        for r in records:
            value = getattr(r, field_name, None)
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            cells.append({"legislation_id": r.id, "value": value})
        matrix.append({"field": field_name, "cells": cells})

    return {
        "fields": fields,
        "columns": columns,
        "matrix": matrix,
        "column_count": len(columns),
    }


def export_comparison_excel(matrix_payload: dict) -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Regulatory Comparison"

    columns = matrix_payload["columns"]
    header = ["Field"] + [
        f"{c['jurisdiction']} | {c['code']}" for c in columns
    ]
    ws.append(header)

    for row in matrix_payload["matrix"]:
        ws.append(
            [row["field"]] + [cell.get("value") or "" for cell in row["cells"]]
        )

    out = BytesIO()
    wb.save(out)
    return out.getvalue()
