from core.authentication.models import Passenger, User, Address, StudentData
from core.authentication.serializers.infra import (
    PassengerCreateSerializer,
    PassengerReadSerializer,
    StudentDataSerializer
)
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

def list_passengers(request):
    passengers = Passenger.objects.select_related('user').prefetch_related('address').all()
    serializer = PassengerReadSerializer(passengers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def retrieve_passenger(request, pk):
    try:
        passenger = Passenger.objects.select_related('user').prefetch_related('address').get(pk=pk)
    except Passenger.DoesNotExist:
        return Response({'detail': 'Passageiro não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PassengerReadSerializer(passenger)
    return Response(serializer.data, status=status.HTTP_200_OK)

@transaction.atomic
def create_passenger(request):
    serializer = PassengerCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    user_data = validated_data.pop('user')
    addresses_data = request.data.pop('addresses', [])
    student_data = validated_data.pop('student_data', None)

    user = User.objects.create_user(
        username=user_data['username'],
        name=user_data['name'],
        email=user_data['email'],
        telephone=user_data['telephone'],
        passage_id=user_data['passage_id'],
        data_of_birth=user_data.get('data_of_birth'),
    )

    passenger = Passenger.objects.create(
        user=user,
        cpf=validated_data['cpf'],
        is_student=validated_data.get('is_student', False)
    )

    address_objs = []
    for addr in addresses_data:
        address = Address.objects.create(**addr)
        address_objs.append(address)
    passenger.address.set(address_objs)

    # Cria os dados do estudante se necessário
    if passenger.is_student and student_data:
        StudentData.objects.create(
            passenger=passenger,
            grade=student_data['grade'],
            registration=student_data['registration']
        )

    output_serializer = PassengerReadSerializer(passenger)
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)
