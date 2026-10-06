from django.conf import settings
from django.db import models


DEFAULT_COMPARE_FIELDS = [
    "scope",
    "enforcement_authority",
    "penalty_max",
    "reporting_obligation",
    "cross_border_rules",
    "status",
    "effective_date",
    "issuing_body",
]


class ComparisonConfig(models.Model):
    """Saved multi-jurisdiction comparison configuration."""

    name = models.CharField(max_length=128)
    topic = models.CharField(max_length=64, blank=True)
    jurisdictions = models.JSONField(default=list)
    fields = models.JSONField(default=list)
    legislation_ids = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comparison_configs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name
