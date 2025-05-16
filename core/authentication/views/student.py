from rest_framework import viewsets

from core.authentication.models import Student
from core.authentication.serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
