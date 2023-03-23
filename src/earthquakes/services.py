from dataclasses import asdict
from typing import List

from scipy.spatial import distance

from earthquakes.dataclasses import CityDTO
from earthquakes.repository import EarthquakeRepository, earthquake_repo

from .clients import EarthquakeDTO, USGSClient, usgs_client


class ClosestEarthquakeFinder:
    def __init__(self):
        self.earthquake_repo: EarthquakeRepository = earthquake_repo
        self.usgs_client: USGSClient = usgs_client

    def execute(self, cities: List[CityDTO], start_time: str, end_time: str) -> EarthquakeDTO:
        usgs_data = self._get_earthquakes(start_time, end_time)
        if not usgs_data:
            return None
        for city_dto in cities:
            saved_earthquake = self._get_from_database(city_dto.id, start_time, end_time)
            if saved_earthquake:
                city_dto.closest_earthquake = saved_earthquake
                continue
            closest_earthquake = self._get_closest_quake(city_dto, usgs_data)
            self._save_closest_earthquake(closest_earthquake, city_dto.id)
            city_dto.closest_earthquake = saved_earthquake
        return cities

    def _get_from_database(self, city_id: int, start_time: str, end_time: str) -> EarthquakeDTO:
        qset = self.earthquake_repo.get_by_attr(
            city__id=city_id, search_range=dict(start_time=start_time, end_time=end_time)
        ).first()
        if not qset:
            return None
        return EarthquakeDTO(
            place=qset.place,
            date=qset.date,
            search_range=qset.search_range,
            latitude=qset.latitude,
            longitude=qset.longitude,
            magnitude=qset.magnitude,
        )

    def _save_closest_earthquake(self, earthquake: EarthquakeDTO, city_id: int) -> None:
        quake_data = asdict(earthquake)
        stored_quake = self.earthquake_repo.get_by_attr(**quake_data).first()
        if stored_quake:
            self.earthquake_repo.add_related_related_obj(stored_quake, city__id=city_id)
        else:
            new_quake = self.earthquake_repo.create(**quake_data)
            self.earthquake_repo.add_related_related_obj(new_quake, city__id=city_id)

    def _get_earthquakes(self, start_time: str, end_time: str) -> List[EarthquakeDTO]:
        return self.usgs_client.get_earthquakes(start_time, end_time)

    def _get_closest_quake(self, city: CityDTO, quakes: List[EarthquakeDTO]) -> EarthquakeDTO:
        node = (city.latitude, city.longitude)
        nodes = [(q.latitude, q.longitude) for q in quakes]
        closest_index = distance.cdist([node], nodes).argmin()
        return quakes[closest_index]


earthquake_finder_service = ClosestEarthquakeFinder()
