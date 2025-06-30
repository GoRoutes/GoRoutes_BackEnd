import django_filters
from core.authentication.models import User

class ResponsibleByStudentsFilter(django_filters.FilterSet):
    responsible_id = django_filters.NumberFilter(field_name='passenger__student_data__responsible__id')

    class Meta:
        model = User
        fields = ['responsible_id']
