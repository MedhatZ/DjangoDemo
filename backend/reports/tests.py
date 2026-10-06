"""
Unit tests for inventory reporting & comparison matrix logic.
Run: python manage.py test reports comparisons
"""
from datetime import date

from django.test import TestCase

from comparisons.services import build_comparison_matrix, resolve_records
from legislation.models import Legislation
from reports.services import (
    InventoryFilterParams,
    apply_inventory_filters,
    build_aggregates,
    build_inventory_report,
    export_inventory_csv,
    export_inventory_excel,
    params_from_query,
)


def _make(**kwargs):
    defaults = {
        "code": kwargs.pop("code"),
        "title": "Test Act",
        "jurisdiction": "Germany",
        "topic": "AI",
        "status": "Active",
        "issuing_body": "Test Body",
        "scope": "Scope A",
        "enforcement_authority": "Auth A",
        "penalty_max": "EUR 1M",
        "reporting_obligation": "Annual",
        "cross_border_rules": "EU",
        "effective_date": date(2024, 1, 1),
    }
    defaults.update(kwargs)
    return Legislation.objects.create(**defaults)


class InventoryReportingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.de_ai = _make(code="T-DE-AI", jurisdiction="Germany", topic="AI", status="Active")
        cls.fr_ai = _make(
            code="T-FR-AI",
            jurisdiction="France",
            topic="AI",
            status="Proposed",
            scope="Scope B",
        )
        cls.uk_dp = _make(
            code="T-UK-DP",
            jurisdiction="UK",
            topic="Data Protection",
            status="Active",
        )
        cls.de_pay_rep = _make(
            code="T-DE-PAY",
            jurisdiction="Germany",
            topic="Payments",
            status="Repealed",
        )

    def test_filter_by_jurisdiction_and_topic(self):
        params = InventoryFilterParams(jurisdiction="Germany", topic="AI")
        report = build_inventory_report(params)
        self.assertEqual(report.total, 1)
        self.assertEqual(report.rows[0]["code"], "T-DE-AI")

    def test_exclude_ids(self):
        params = InventoryFilterParams(
            jurisdiction="Germany",
            exclude_ids=[self.de_ai.id],
        )
        report = build_inventory_report(params)
        codes = {r["code"] for r in report.rows}
        self.assertNotIn("T-DE-AI", codes)
        self.assertIn("T-DE-PAY", codes)

    def test_include_ids_only(self):
        params = InventoryFilterParams(include_ids=[self.fr_ai.id, self.uk_dp.id])
        report = build_inventory_report(params)
        self.assertEqual(report.total, 2)

    def test_aggregates_by_status(self):
        qs = apply_inventory_filters(
            Legislation.objects.all(), InventoryFilterParams()
        )
        agg = build_aggregates(qs)
        self.assertEqual(agg["total"], 4)
        self.assertEqual(agg["by_status"].get("Active"), 2)
        self.assertEqual(agg["by_status"].get("Proposed"), 1)
        self.assertEqual(agg["by_status"].get("Repealed"), 1)

    def test_ordering(self):
        params = InventoryFilterParams(ordering="-status,code")
        report = build_inventory_report(params)
        statuses = [r["status"] for r in report.rows]
        # Repealed / Proposed / Active lexicographic reverse depends on values;
        # just assert deterministic length and first row matches order_by
        self.assertEqual(len(statuses), 4)
        ordered = list(
            Legislation.objects.order_by("-status", "code").values_list(
                "code", flat=True
            )
        )
        self.assertEqual([r["code"] for r in report.rows], ordered)

    def test_params_from_query_parses_ids(self):
        params = params_from_query(
            {
                "jurisdiction": "UK",
                "exclude_ids": f"{self.de_ai.id},{self.fr_ai.id}",
                "ordering": "code",
            }
        )
        self.assertEqual(params.jurisdiction, "UK")
        self.assertEqual(params.exclude_ids, [self.de_ai.id, self.fr_ai.id])

    def test_csv_export_contains_header_and_row(self):
        report = build_inventory_report(InventoryFilterParams(topic="AI"))
        raw = export_inventory_csv(report.rows).decode("utf-8-sig")
        self.assertIn("code,title,jurisdiction", raw)
        self.assertIn("T-DE-AI", raw)

    def test_excel_export_nonempty(self):
        report = build_inventory_report(InventoryFilterParams())
        payload = export_inventory_excel(report.rows)
        self.assertTrue(payload[:2] == b"PK")  # zip/xlsx signature


class ComparisonMatrixTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.de = _make(
            code="C-DE",
            jurisdiction="Germany",
            topic="AI",
            scope="DE scope",
            penalty_max="EUR 10M",
        )
        cls.fr = _make(
            code="C-FR",
            jurisdiction="France",
            topic="AI",
            scope="FR scope",
            penalty_max="EUR 8M",
        )
        cls.uk = _make(
            code="C-UK",
            jurisdiction="UK",
            topic="AI",
            scope="UK scope",
            penalty_max="GBP 10M",
        )

    def test_resolve_multiple_jurisdictions(self):
        records = resolve_records(
            jurisdictions=["Germany", "France"],
            topic="AI",
        )
        codes = {r.code for r in records}
        self.assertEqual(codes, {"C-DE", "C-FR"})

    def test_matrix_side_by_side_fields(self):
        records = resolve_records(jurisdictions=["Germany", "France", "UK"], topic="AI")
        matrix = build_comparison_matrix(records, fields=["scope", "penalty_max"])
        self.assertEqual(matrix["column_count"], 3)
        self.assertEqual(len(matrix["matrix"]), 2)
        scope_row = matrix["matrix"][0]
        self.assertEqual(scope_row["field"], "scope")
        values = [c["value"] for c in scope_row["cells"]]
        self.assertIn("DE scope", values)
        self.assertIn("FR scope", values)
        self.assertIn("UK scope", values)

    def test_requires_at_least_structured_fields(self):
        records = [self.de, self.fr]
        matrix = build_comparison_matrix(records, fields=None)
        self.assertGreaterEqual(len(matrix["fields"]), 5)
        self.assertEqual(len(matrix["columns"]), 2)
