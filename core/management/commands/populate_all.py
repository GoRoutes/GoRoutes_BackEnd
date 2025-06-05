from django.core.management.base import BaseCommand
from core.authentication.models import (
    User, Address, Driver, Passenger, Responsible, StudentData
)
from faker import Faker
import random

fake = Faker('pt_BR')

class Command(BaseCommand):
    help = "Popula o banco de dados com dados fictícios"

    def handle(self, *args, **kwargs):
        self.stdout.write("Populando dados...")

        # Usuários
        users = []
        for _ in range(10):
            user = User.objects.create(
                username=fake.user_name(),
                name=fake.name(),
                email=fake.unique.email(),
                telephone=fake.phone_number(),
                data_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70)
            )
            users.append(user)

        addresses = []
        for _ in range(15):
            addr = Address.objects.create(
                cep=fake.postcode(),
                street=fake.street_name(),
                number=str(fake.building_number()),
                complement=fake.word() if random.choice([True, False]) else None,
                neighborhood=fake.city_suffix(),
                city=fake.city(),
                state=fake.state_abbr(),
                is_main=random.choice([True, False])
            )
            addresses.append(addr)

        responsibles = []
        passengers = []
        students = []
        drivers = []

        for i in range(3):
            responsible = Responsible.objects.create(
                cpf=fake.cpf(),
                user=users[i]
            )
            responsibles.append(responsible)

        for i in range(3, 6):
            passenger = Passenger.objects.create(
                cpf=fake.cpf(),
                user=users[i],
                is_student=False
            )
            passenger.address.add(*random.sample(addresses, random.randint(1, 2)))
            passengers.append(passenger)

        for i in range(6, 8):
            responsible = random.choice(responsibles)
            passenger = Passenger.objects.create(
                cpf=fake.cpf(),
                user=users[i],
                is_student=True
            )
            passenger.address.add(*random.sample(addresses, random.randint(1, 2)))

            StudentData.objects.create(
                passenger=passenger,
                grade=random.choice(['1º ano', '2º ano', '3º ano']),
                registration=fake.numerify(text='##########'),
                responsible=responsible
            )
            students.append(passenger)

        for i in range(8, 10):
            driver = Driver.objects.create(
                cnh=fake.numerify(text='###########'),
                cpf=fake.cpf(),
                user=users[i]
            )
            driver.adresses.add(*random.sample(addresses, random.randint(1, 2)))
            drivers.append(driver)

        self.stdout.write(self.style.SUCCESS("Dados populados com sucesso!"))
