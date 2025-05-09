from rest_framework import serializers

from core.authentication.models import Parent, Student
from core.authentication.serializers import UserSerializer, StudentSerializer



class ParentListSerializer(serializers.ModelSerializer):
    children = StudentSerializer(many=True)
    user = UserSerializer()
    
    class Meta:
        model = Parent
        fields = ['id', 'user', 'children']

class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    students = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Student.objects.all(), source='children', required=False
    )

    class Meta:
        model = Parent
        fields = ['id', 'user', 'students']
        depth = 1

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        students_data = validated_data.pop('children', [])
        parent = Parent.objects.create(user=user, **validated_data)
        parent.children.set(students_data)
        return parent
    
    def update(self, instance, validated_data):
        students_data = validated_data.pop('children', None)
        if students_data is not None:
            instance.children.set(students_data)
        return super().update(instance, validated_data)
