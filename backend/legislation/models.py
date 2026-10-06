from django.db import models


class Jurisdiction(models.TextChoices):
    GERMANY = "Germany", "Germany"
    FRANCE = "France", "France"
    UK = "UK", "UK"


class Topic(models.TextChoices):
    AI = "AI", "AI"
    DATA_PROTECTION = "Data Protection", "Data Protection"
    PAYMENTS = "Payments", "Payments"


class Status(models.TextChoices):
    ACTIVE = "Active", "Active"
    PROPOSED = "Proposed", "Proposed"
    REPEALED = "Repealed", "Repealed"


class Legislation(models.Model):
    """
    Mock legislative / regulatory record for the reporting POC.
    Fields mirror typical inventory + comparison structured attributes.
    """

    code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=32, choices=Jurisdiction.choices)
    topic = models.CharField(max_length=64, choices=Topic.choices)
    status = models.CharField(max_length=32, choices=Status.choices)
    effective_date = models.DateField(null=True, blank=True)
    last_amended = models.DateField(null=True, blank=True)
    issuing_body = models.CharField(max_length=128)
    summary = models.TextField(blank=True)
    # Structured fields used in side-by-side comparison
    scope = models.CharField(max_length=255, blank=True)
    enforcement_authority = models.CharField(max_length=128, blank=True)
    penalty_max = models.CharField(max_length=128, blank=True)
    reporting_obligation = models.CharField(max_length=255, blank=True)
    cross_border_rules = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["jurisdiction", "topic", "code"]
        verbose_name_plural = "legislation"

    def __str__(self):
        return f"{self.code} — {self.title}"
