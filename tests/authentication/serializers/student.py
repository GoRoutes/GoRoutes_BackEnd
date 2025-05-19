from rest_framework import serializers

from core.authentication.models import Student

from core.authentication.serializers.user import UserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'grade']
        read_only_fields = ['id']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(instance=instance.user, data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        instance.user = user
        instance.save()
        return instance 
