from rest_framework import serializers

from core.authentication.models import Parent
from core.authentication.serializers import UserSerializer, StudentSerializer

class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    students = StudentSerializer(many=True)

    class Meta:
        model = Parent
        fields = ['id', 'user', 'students']