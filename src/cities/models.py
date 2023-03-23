from django.db import models

# Create your models here.
from django.db.models import CharField, FloatField, Model


class City(Model):

    name = CharField(max_length=50, unique=True)
    state = CharField(max_length=50)
    country = CharField(max_length=2)
    latitude = FloatField(default=0.0)
    longitude = FloatField(default=0.0)

    def __str__(self):
        return self.name
