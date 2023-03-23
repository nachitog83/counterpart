from app.repositories import BaseRepository

from cities.models import City

"""
City repository inherited from BaseRepository.
We could define specific behaviour for city domain logic here

"""


class CityRepository(BaseRepository):
    pass


city_repo = CityRepository(City)
