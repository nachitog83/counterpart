from dataclasses import asdict

from cities.services import city_handler
from django.forms.models import model_to_dict
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from earthquakes.services import CityDTO, earthquake_finder_service

# Create your views here.

REQUIRED_POST_REQUEST_DATA = ["start_time", "end_time"]


class ClosesEarthquakeView(APIView):
    def get_cities(self):
        try:
            cities = city_handler.get_all()
            return [CityDTO(**model_to_dict(city)) for city in cities]
        except city_handler.city_repo.model.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        if not all(attr in request.data.keys() for attr in REQUIRED_POST_REQUEST_DATA):
            return Response("Wrong request body data", status=status.HTTP_400_BAD_REQUEST)
        results = []
        start_time = request.data["start_time"]
        end_time = request.data["end_time"]
        cities = self.get_cities()
        cities = earthquake_finder_service.execute(cities, start_time, end_time)
        if not cities:
            return Response("No results found", status=status.HTTP_404_NOT_FOUND)
        for city in cities:
            city_data = asdict(city)
            results.append(city_data)
        return Response(results, status=status.HTTP_200_OK)
