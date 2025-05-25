from django.db import models
from core.authentication.models import User, Address, Responsible


class Passenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passenger')
    cpf = models.CharField(max_length=11, unique=True)
    is_student = models.BooleanField(default=False)
    address = models.ManyToManyField(Address, related_name='passenger', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.cpf}'
    

class StudentData(models.Model):
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE, related_name='student_data')
    grade = models.CharField(max_length=50)
    registration = models.CharField(max_length=20, unique=True)
    responsible = models.ForeignKey(Responsible, on_delete=models.CASCADE, related_name='student_data', null=True, blank=True)

    def __str__(self):
        return f'{self.passenger.user.username} - {self.grade}'
