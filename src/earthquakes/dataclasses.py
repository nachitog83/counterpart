from dataclasses import dataclass
from datetime import datetime
from typing import Optional

"""
Dataclasses define to serve as data models and interfaces
between model objects and services

"""


@dataclass
class EarthquakeDTO:

    # Dataclass that defines the fields we'll need to create an
    # instance of Closest Earthquake

    place: str
    date: datetime
    search_range: dict
    latitude: float
    longitude: float
    magnitude: float


@dataclass
class CityDTO:

    # Dataclass to serve as interface for City Model object.

    id: int
    name: str
    state: str
    country: str
    latitude: float
    longitude: float
    closest_earthquake: Optional[EarthquakeDTO] = None
