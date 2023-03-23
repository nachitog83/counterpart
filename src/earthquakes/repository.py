from app.repositories import BaseRepository

from earthquakes.models import ClosestEarthquake

"""
EarthquakeRepository repository inherited from BaseRepository.
We could define specific behaviour for closest earthquake domain logic here

"""


class EarthquakeRepository(BaseRepository):
    pass


earthquake_repo = EarthquakeRepository(ClosestEarthquake)
