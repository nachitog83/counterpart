from dataclasses import asdict
from typing import List

from geopy.geocoders import Nominatim

from cities.dataclasses import CityCreateDTO
from cities.models import City
from cities.repository import CityRepository, city_repo

"""
City Model Handler service: to be used as interface between our
infrastructure (database through repository) and domain logic.

Domain logic in this particular case is using the geolocator
library to get cities coordinates and save them to database.

City repo is injected as a service attribute.
Handler is instanciated to be used or injected in our application
layer (REST views)

"""


class CityModelHandler:
    def __init__(self):
        self.city_repo: CityRepository = city_repo

    def get_by_attribute(self, **kwargs) -> City:
        return self.city_repo.get_by_attr(**kwargs)

    def get_all(self) -> List[City]:
        return self.city_repo.get_all()

    def create(self, dto: CityCreateDTO) -> City:
        point = self._get_city_coords(dto)
        return self.city_repo.create(**asdict(dto), latitude=point[0], longitude=point[1])

    def save(self, obj: City) -> City:
        return self.city_repo.save(obj)

    @staticmethod
    def _get_city_coords(dto) -> List[float]:
        geolocator = Nominatim(user_agent="MyApp")
        loc = geolocator.geocode(f"{dto.name}, {dto.country}")
        return [loc.latitude, loc.longitude]


city_handler = CityModelHandler()
