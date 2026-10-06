from rest_framework import serializers

from .models import DEFAULT_COMPARE_FIELDS, ComparisonConfig


class ComparisonConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparisonConfig
        fields = [
            "id",
            "name",
            "topic",
            "jurisdictions",
            "fields",
            "legislation_ids",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_jurisdictions(self, value):
        if not isinstance(value, list) or len(value) < 1:
            raise serializers.ValidationError(
                "Select at least one jurisdiction for comparison."
            )
        return value

    def validate_fields(self, value):
        if not value:
            return list(DEFAULT_COMPARE_FIELDS)
        return value
