import unittest.mock as mock

import pytest
from django.test import Client
from django.urls import reverse

from cities.models import City
from cities.services import CityCreateDTO, city_handler

# Create your tests here.

client = Client()


@pytest.mark.parametrize(
    "raise_errors, kwargs",
    [
        (False, dict(name="Los Angeles", state="California", country="US")),
        (True, dict(name="x" * 51, state="California", country="US")),
        (True, dict(name="Los Angeles", state="x" * 51, country="US")),
        (True, dict(name="Los Angeles", state="California", country="XXX")),
    ],
)
def test_create_city_dto(raise_errors, kwargs):
    if raise_errors:
        with pytest.raises(Exception):
            dto = CityCreateDTO(**kwargs)
    else:
        dto = CityCreateDTO(**kwargs)
        assert dto


@pytest.fixture
def city_dto():
    return CityCreateDTO(name="Los Angeles", state="California", country="US")


@mock.patch.object(city_handler, "_get_city_coords", return_value=[1.0, 0.1])
@pytest.mark.django_db
def test_city_handler_create(mocked_fn, city_dto):
    city_handler.create(city_dto)
    obj = City.objects.filter(pk=1).first()
    assert obj.name == city_dto.name
    assert obj.state == city_dto.state
    assert obj.country == city_dto.country
    assert obj.latitude == 1.0
    assert obj.longitude == 0.1


@pytest.mark.vcr()
def test_get_city_coords(city_dto):
    results = city_handler._get_city_coords(city_dto)
    assert results[0] == 34.0536909
    assert results[1] == -118.242766


@pytest.fixture
def bulk_cities():
    City.objects.bulk_create(
        [
            City(id=1, name="Los Angeles", state="California", country="US", latitude=1.0, longitude=0.1),
            City(id=2, name="San Francisco", state="California", country="US", latitude=1.2, longitude=2.1),
            City(id=3, name="Tokyo", state="Kanto", country="JP", latitude=1.3, longitude=3.1),
        ]
    )
    yield
    City.objects.all().delete()


@pytest.mark.django_db
def test_get_all_cities_view(bulk_cities):
    response = client.get(reverse("get_cities"))
    assert len(response.data) == 3
    assert response.data[0]["name"] == "Los Angeles"
    assert response.data[1]["name"] == "San Francisco"
    assert response.data[2]["name"] == "Tokyo"


@pytest.mark.django_db
def test_get_one_cities_view(bulk_cities):
    response = client.get(reverse(f"get_city", args=[1]))
    assert response.data["name"] == "Los Angeles"


@pytest.mark.parametrize(
    "status_code, kwargs",
    [
        (201, dict(name="Los Angeles", state="California", country="US")),
        (400, dict(name="Los Angeles", state="California")),
        (400, dict(name="Los Angeles", state="California", country="US", random="random")),
    ],
)
@mock.patch(
    "cities.views.city_handler.create",
    return_value=City(id=1, name="Los Angeles", state="California", country="US", latitude=1.0, longitude=0.1),
)
def test_city_create_view_success(mocked_fn, status_code, kwargs):
    response = client.post(reverse("create_city"), kwargs)
    assert response.status_code == status_code
