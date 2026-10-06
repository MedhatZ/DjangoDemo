import django_filters

from .models import Legislation


class LegislationFilter(django_filters.FilterSet):
    jurisdiction = django_filters.CharFilter(lookup_expr="iexact")
    topic = django_filters.CharFilter(lookup_expr="iexact")
    status = django_filters.CharFilter(lookup_expr="iexact")
    jurisdiction__in = django_filters.BaseInFilter(
        field_name="jurisdiction", lookup_expr="in"
    )
    topic__in = django_filters.BaseInFilter(field_name="topic", lookup_expr="in")
    status__in = django_filters.BaseInFilter(field_name="status", lookup_expr="in")
    id__in = django_filters.BaseInFilter(field_name="id", lookup_expr="in")
    id__notin = django_filters.BaseInFilter(
        field_name="id", lookup_expr="in", exclude=True
    )

    class Meta:
        model = Legislation
        fields = ["jurisdiction", "topic", "status"]
