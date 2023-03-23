from datetime import datetime, timezone

import requests
from django.core.cache import cache

from earthquakes.dataclasses import EarthquakeDTO

"""
USGS Client define to act as a client service to connect to
USGS database and get earthquake data around the world.

This USGSClient class is instanciated in an object to be injected
into any other service that may need it's attributes.

Search results are persisted to Redis Cache database for a period
of 180 seconds, using date range fstring as key.

"""


class USGSClient:
    URL = r"https://earthquake.usgs.gov/fdsnws/event/1/query?"
    FORMAT = "geojson"
    ORDER_BY = "time"
    MIN_MAGNITUDE = "5"
    CACHE_TTL = 180

    def get_earthquakes(self, start_time: str, end_time: str):
        cache_key = f"{start_time}_{end_time}"
        if cache_key in cache:
            data = cache.get(cache_key)
        else:
            params = {
                "format": self.FORMAT,
                "starttime": start_time,
                "endtime": end_time,
                "minmagnitude": self.MIN_MAGNITUDE,
                "orderby": self.ORDER_BY,
            }
            response_data = requests.get(self.URL, params=params)
            if response_data.status_code != 200:
                raise Exception(response_data.text)
            data = response_data.json()["features"]
            if not data:
                return []
            cache.set(cache_key, data, timeout=self.CACHE_TTL)
        return [
            EarthquakeDTO(
                place=eq["properties"]["place"],
                date=datetime.fromtimestamp(eq["properties"]["time"] / 1000.0, timezone.utc),
                search_range=dict(start_time=start_time, end_time=end_time),
                latitude=eq["geometry"]["coordinates"][0],
                longitude=eq["geometry"]["coordinates"][1],
                magnitude=eq["properties"]["mag"],
            )
            for eq in data
        ]


usgs_client = USGSClient()
