from rest_framework import serializers
from core.authentication.serializers.infra import (
    AddressReadSerializer, 
    AddressWriterSerializer, 
    UserWriterSerializer, 
    UserReadSerializer
)


class StudentDataSerializer(serializers.Serializer):
    grade = serializers.CharField(max_length=50)
    registration = serializers.CharField(max_length=20)

class PassengerCreateSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=14)
    user = UserWriterSerializer()
    is_student = serializers.BooleanField(default=False)
    addresses = AddressWriterSerializer(many=True, required=False)
    student_data = StudentDataSerializer(required=False)

    def validate(self, data):
        is_student = data.get('is_student', False)
        student_data = data.get('student_data')

        if is_student and not student_data:
            raise serializers.ValidationError({
                'student_data': 'Dados do estudante são obrigatórios quando is_student é True.'
            })
        return data

class PassengerReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    is_student = serializers.BooleanField()
    user = UserReadSerializer()
    address = AddressReadSerializer(many=True)
    student_data = StudentDataSerializer(required=False)


