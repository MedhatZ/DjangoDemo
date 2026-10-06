from rest_framework import serializers

from .models import Legislation


class LegislationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislation
        fields = [
            "id",
            "code",
            "title",
            "jurisdiction",
            "topic",
            "status",
            "effective_date",
            "last_amended",
            "issuing_body",
            "summary",
            "scope",
            "enforcement_authority",
            "penalty_max",
            "reporting_obligation",
            "cross_border_rules",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
