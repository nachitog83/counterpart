from django.db.models import (
    CharField,
    DateTimeField,
    FloatField,
    JSONField,
    ManyToManyField,
    Model,
)


def search_default():
    return dict(start_time="", end_time="")


# Create your models here.
class ClosestEarthquake(Model):

    city = ManyToManyField("cities.City")
    place = CharField(max_length=50)
    date = DateTimeField()
    search_range = JSONField("search_range", default=search_default, unique=True)
    latitude = FloatField(default=0.0)
    longitude = FloatField(default=0.0)
    magnitude = FloatField(default=0.0)

    def __str__(self) -> str:
        return f"{self.place}_{self.search_range['start_time']}_{self.search_range['end_time']}"
