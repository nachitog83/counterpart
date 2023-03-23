from dataclasses import dataclass, fields
from typing import Optional

"""
Dataclasses define to serve as data models and interfaces
between model objects and services

"""


@dataclass
class CityCreateDTO:

    # Dataclass that defines the fields we'll need to create an instance of City

    name: str
    country: str
    state: Optional[str] = ""

    def __post_init__(self):
        field_length = dict(name=50, state=50, country=2)
        for field in fields(self):
            length = field_length.get(field.name)
            if len(getattr(self, field.name)) > length:
                raise Exception(f"{field.name} field length must not be greater than {length}")
