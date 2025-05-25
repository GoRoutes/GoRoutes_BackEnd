from django.db import models

class Address(models.Model):
    cep = models.CharField(max_length=9, null=False, blank=False)
    street = models.CharField(max_length=100, null=False, blank=False)
    number = models.CharField(max_length=10, null=False, blank=False)
    complement = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=2, null=False, blank=False)
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.street}, {self.number}, {self.neighborhood}, {self.city}, {self.state}'

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'