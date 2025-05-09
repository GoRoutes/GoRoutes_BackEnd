from rest_framework import serializers

from core.authentication.models import Student

from core.authentication.serializers.user import UserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'grade']