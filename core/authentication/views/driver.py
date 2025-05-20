from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from core.authentication.models import User, Address, Driver
from core.authentication.serializers.infra import DriverReadSerializer, DriverCreateSerializer

class DriverViewSet(ViewSet):
    """
    ViewSet para gerenciar motoristas.
    Permite listar, criar, atualizar e excluir motoristas.
    """
    
    def list(self, request):
        drivers = Driver.objects.select_related('user').prefetch_related('adresses').all()
        serializer = DriverReadSerializer(drivers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            driver = Driver.objects.select_related('user').prefetch_related('adresses').get(pk=pk)
        except Driver.DoesNotExist:
            return Response({'detail': 'Motorista não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DriverReadSerializer(driver)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request):
        serializer = DriverCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        user_data = validated_data.pop('user')
        addresses_data = request.data.pop('addresses', [])

        user = User.objects.create_user(
            username=user_data['username'],
            name=user_data['name'],
            email=user_data['email'],
            telephone=user_data['telephone'],
            passage_id=user_data['passage_id'],
            data_of_birth=user_data.get('data_of_birth'),
        )

        driver = Driver.objects.create(
            user=user,
            cnh=validated_data['cnh'],
            cpf=validated_data['cpf'],
            is_active=validated_data.get('is_active', True)
        )

        address_objs = []
        for addr in addresses_data:
            address = Address.objects.create(**addr)
            address_objs.append(address)

        driver.adresses.set(address_objs)

        output_serializer = DriverReadSerializer(driver)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
