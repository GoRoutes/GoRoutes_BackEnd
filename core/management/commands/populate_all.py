from django.core.management.base import BaseCommand
from core.authentication.models import (
    User, Address, Driver, Passenger, Responsible, StudentData
)
from faker import Faker
import random
import os
import json

# Caminho para o JSON com os alunos
data_file_path = os.path.join(os.path.dirname(__file__), 'data/students.json')

fake = Faker('pt_BR')

class Command(BaseCommand):
    help = "Popula o banco de dados com dados fictícios e reais dos alunos do IFC"

    def handle(self, *args, **kwargs):
        self.stdout.write("Populando dados...")

        with open(data_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        responsibles = []

        # Criar o responsável fixo Anthony
        anthony_user = User.objects.create(
            username='anthony',
            name='Anthony',
            email='anthony@gmail.com',
            telephone='11999999999',
            data_of_birth='1980-01-01'
        )
        anthony_user.set_password('123456')
        anthony_user.save()

        anthony_responsible = Responsible.objects.create(
            cpf="11345562926",
            user=anthony_user
        )
        responsibles.append(anthony_responsible)

        for _ in range(2):
            user = User.objects.create(
                username=fake.user_name(),
                name=fake.name(),
                email=fake.unique.email(),
                telephone=fake.phone_number(),
                data_of_birth=fake.date_of_birth(minimum_age=30, maximum_age=60)
            )
            responsible = Responsible.objects.create(
                cpf=fake.cpf(),
                user=user
            )
            responsibles.append(responsible)

        for entry in data:
            u = entry["user"]
            user = User.objects.create(
                username=u["username"],
                name=u["name"],
                email=u["email"],
                telephone=u["telephone"],
                data_of_birth=u["data_of_birth"]
            )
            user.set_password(u["password"])
            user.save()

            # Endereço principal
            address_data = entry["addresses"][0]
            address = Address.objects.create(
                street=address_data["street"],
                number=address_data["number"],
                neighborhood=address_data["neighborhood"],
                city=address_data["city"],
                state=address_data["state"],
                cep=address_data["cep"],
                is_main=address_data["is_main"]
            )

            # Passageiro
            passenger = Passenger.objects.create(
                cpf=entry["cpf"],
                user=user,
                is_student=entry["is_student"]
            )
            passenger.address.add(address)

            # Se for estudante, vincula StudentData com Anthony
            if entry["is_student"]:
                StudentData.objects.create(
                    passenger=passenger,
                    grade=entry["student_data"]["grade"],
                    registration=entry["student_data"]["registration"],
                    responsible=anthony_responsible  
                )

        # Criar motoristas fictícios
        for _ in range(2):
            user = User.objects.create(
                username=fake.user_name(),
                name=fake.name(),
                email=fake.unique.email(),
                telephone=fake.phone_number(),
                data_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=60)
            )
            driver = Driver.objects.create(
                cnh=fake.numerify(text='###########'),
                cpf=fake.cpf(),
                user=user
            )

            for _ in range(random.randint(1, 2)):
                address = Address.objects.create(
                    street=fake.street_name(),
                    number=fake.building_number(),
                    neighborhood=fake.city_suffix(),
                    city=fake.city(),
                    state=fake.state_abbr(),
                    cep=fake.postcode(),
                    is_main=random.choice([True, False])
                )
                driver.adresses.add(address)

        self.stdout.write(self.style.SUCCESS("Dados populados com sucesso!"))
