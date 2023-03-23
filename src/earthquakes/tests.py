from datetime import datetime, timezone
from unittest import mock

import pytest
import vcr
from cities.models import City
from django.test import Client
from django.urls import reverse

from earthquakes.clients import EarthquakeDTO, usgs_client
from earthquakes.models import ClosestEarthquake
from earthquakes.services import CityDTO, earthquake_finder_service

# Create your tests here.

client = Client()


@pytest.mark.vcr
def test_usgs_client_sucesss():
    start_time = "2021-06-07"
    end_time = "2021-07-07"

    results = usgs_client.get_earthquakes(start_time, end_time)
    assert results


@pytest.mark.vcr
def test_usgs_client_fail():
    start_time = 1
    end_time = 2

    with pytest.raises(Exception):
        results = usgs_client.get_earthquakes(start_time, end_time)


@pytest.fixture
def city():
    return City.objects.create(
        id=1, name="Los Angeles", state="California", country="US", latitude=34.053691, longitude=-118.242766
    )


@pytest.fixture
def closest_earthquake():
    eq = ClosestEarthquake.objects.create(
        id=1,
        place="South Sandwich Islands region",
        date=datetime(2021, 6, 13, 7, 24, 46, 852000),
        latitude=-25.703,
        longitude=-60.8818,
        search_range=dict(start_time="2021-06-07", end_time="2021-07-07"),
        magnitude=5,
    )
    eq.city.add(1)
    eq.save()
    return eq


@pytest.fixture
def city_dto():
    return CityDTO(
        id=1, name="Los Angeles", state="California", country="US", latitude=34.053691, longitude=-118.242766
    )


@pytest.fixture
def earthquake_dto():
    return EarthquakeDTO(
        place="South Sandwich Islands region",
        date=datetime(2021, 6, 13, 7, 24, 46, 852000, tzinfo=timezone.utc),
        latitude=-25.703,
        longitude=-60.8818,
        search_range=dict(start_time="2021-06-07", end_time="2021-07-07"),
        magnitude=5,
    )


@pytest.mark.django_db
def test_get_from_db(city, closest_earthquake):
    start_time = "2021-06-07"
    end_time = "2021-07-07"
    saved_eq = earthquake_finder_service._get_from_database(city.id, start_time, end_time)
    assert saved_eq.place == closest_earthquake.place


@pytest.mark.django_db
def test_save_new_closest_earthquake(city, earthquake_dto):
    assert len(ClosestEarthquake.objects.all()) == 0
    earthquake_finder_service._save_closest_earthquake(earthquake_dto, city.id)
    assert len(ClosestEarthquake.objects.all()) == 1


@pytest.mark.django_db
def test_add_new_closest_earthquake_for_city(city, closest_earthquake, earthquake_dto):
    assert len(ClosestEarthquake.objects.all()) == 1
    earthquake_finder_service._save_closest_earthquake(earthquake_dto, city.id)
    assert len(ClosestEarthquake.objects.all()) == 1


def test_get_closest_earthquake(earthquake_dto, city_dto):
    with vcr.use_cassette("earthquakes/cassettes/test_usgs_client_sucesss.yaml"):
        data = earthquake_finder_service._get_earthquakes(**earthquake_dto.search_range)
        closest = earthquake_finder_service._get_closest_quake(city_dto, data)
        assert closest


@pytest.mark.parametrize(
    "status_code, kwargs",
    [
        (200, dict(start_time="2021-06-07", end_time="2021-07-07")),
        (400, dict(random1="Los Angeles", state="California")),
    ],
)
@mock.patch(
    "earthquakes.views.earthquake_finder_service.execute",
    return_value=[
        EarthquakeDTO(
            place="South Sandwich Islands region",
            date="2021-06-13T07:24:46.852000",
            latitude=-25.703,
            longitude=-60.8818,
            search_range=dict(start_time="2021-06-07", end_time="2021-07-07"),
            magnitude=5,
        )
    ],
)
@mock.patch(
    "earthquakes.views.ClosesEarthquakeView.get_cities",
    return_value=[
        CityDTO(id=1, name="Los Angeles", state="California", country="US", latitude=34.053691, longitude=-118.242766)
    ],
)
def test_city_create_view_success(mocked_fn, mocked_fn_2, status_code, kwargs):
    response = client.post(reverse("get_closest"), kwargs)
    assert response.status_code == status_code


@mock.patch(
    "earthquakes.views.earthquake_finder_service.execute",
    return_value=[],
)
@mock.patch(
    "earthquakes.views.ClosesEarthquakeView.get_cities",
    return_value=[
        CityDTO(id=1, name="Los Angeles", state="California", country="US", latitude=34.053691, longitude=-118.242766)
    ],
)
def test_city_create_view_not_found(mocked_fn, mocked_fn_2):
    response = client.post(reverse("get_closest"), dict(start_time="1021-06-07", end_time="1021-07-07"))
    assert response.status_code == 404


@pytest.mark.django_db
def test_execute_with_saved_obj(city_dto, earthquake_dto, city, closest_earthquake):
    result = earthquake_finder_service.execute([city_dto], **earthquake_dto.search_range)
    city_dto.closest_earthquake = closest_earthquake
    assert result == [city_dto]


@pytest.mark.django_db
def test_execute_without_saved_obj(city_dto, earthquake_dto, city):
    result = earthquake_finder_service.execute([city_dto], **earthquake_dto.search_range)
    city_dto.closest_earthquake = closest_earthquake
    assert result == [city_dto]
