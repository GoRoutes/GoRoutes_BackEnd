from core.authentication.models import Responsible
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
    responsible = serializers.PrimaryKeyRelatedField(queryset=Responsible.objects.all(), required=False)

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
    cpf = serializers.CharField()
    is_student = serializers.BooleanField()
    user = UserReadSerializer()
    address = serializers.SerializerMethodField()
    student_data = StudentDataSerializer(required=False)

    def get_address(self, obj):
        main_addresses = obj.address.filter(is_main=True)
        return AddressReadSerializer(main_addresses, many=True).data


