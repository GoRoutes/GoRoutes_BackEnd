from core.authentication.models import User
from rest_framework import serializers
from datetime import date
from rest_framework.response import Response

def validate_unique_user_email(email):
    if User.objects.filter(email=email).exists():
        return Response({
            "error": "Já existe um usuário com este e-mail.",
            "code": "email_already_exists",
            "status": 400
        }, status=400)
    return email

def validate_unique_user_name(name):
    if User.objects.filter(name=name).exists():
        raise serializers.ValidationError({
            "error": "Já existe um usuário com este nome.",
            "code": "name_already_exists",
            "status": 400
        })
    return name

def validate_unique_username(username):
    if User.objects.filter(username=username).exists():
        raise serializers.ValidationError({
            "error": "Já existe um usuário com este nome de usuário (username).",
            "code": "username_already_exists",
            "status": 400
        })
    return username


def validate_max_age(data_of_birth):
    if data_of_birth is None:
        return data_of_birth

    today = date.today()
    age = today.year - data_of_birth.year - (
        (today.month, today.day) < (data_of_birth.month, data_of_birth.day)
    )

    if age > 120:
        raise serializers.ValidationError({
            "error": "A data de nascimento indica idade superior a 120 anos.",
            "code": "age_exceeds_limit",
            "status": 400
        })
    return data_of_birth
