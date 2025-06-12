from core.authentication.models import Address, Responsible, User
from core.authentication.serializers.infra import (
    ResponsibleCreateSerializer,
    ResponsibleReadSerializer,
)
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response


def list_responsibles(request):
    responsibles = Responsible.objects.select_related('user')
    serializer = ResponsibleReadSerializer(responsibles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def retrieve_responsible(request, pk):
    try:
        responsible = Responsible.objects.select_related('user').get(pk=pk)
    except Responsible.DoesNotExist:
        return Response(
            {'detail': 'Responsável não encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ResponsibleReadSerializer(responsible)
    return Response(serializer.data, status=status.HTTP_200_OK)


@transaction.atomic
def create_responsible(request):
    serializer = ResponsibleCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    user_data = validated_data.pop('user')

    user = User.objects.create_user(
        username=user_data['username'],
        name=user_data['name'],
        email=user_data['email'],
        telephone=user_data['telephone'],
        data_of_birth=user_data.get('data_of_birth'),
        password=user_data['password'],
    )

    responsible = Responsible.objects.create(
        user=user,
        cpf=validated_data['cpf'],
    )

    output_serializer = ResponsibleReadSerializer(responsible)
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)


def delete_responsible(request, pk):
    try:
        responsible = Responsible.objects.get(pk=pk)
        user = responsible.user
        user.delete()
        responsible.delete()
        return Response(
            {"detail": "Responsável deletado com sucesso"},
            status=status.HTTP_200_OK,
        )
    except Responsible.DoesNotExist:
        return Response(
            {"detail": "Responsável não encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )