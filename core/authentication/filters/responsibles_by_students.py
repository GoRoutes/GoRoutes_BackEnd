import django_filters
from core.authentication.models import User

class CombinedUserFilter(django_filters.FilterSet):
    is_driver = django_filters.BooleanFilter(method='filter_is_driver')
    responsible_id = django_filters.NumberFilter(field_name='passenger__student_data__responsible__id')
    is_passenger = django_filters.BooleanFilter(method='filter_is_passenger')

    def filter_is_driver(self, queryset, name, value):
        if value:
            return queryset.exclude(driver__isnull=True)
        else:
            return queryset.filter(driver__isnull=True)

    def filter_is_passenger(self, queryset, name, value):
        if value:
            return queryset.exclude(passenger__isnull=True)
        else:
            return queryset.filter(passenger__isnull=True)

    class Meta:
        model = User
        fields = ['is_driver', 'responsible_id', 'is_passenger']
