from django.forms.models import model_to_dict
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cities.services import CityCreateDTO, city_handler

REQUIRED_POST_REQUEST_DATA = ["name", "country"]


class CityDetailView(APIView):
    # City Detail API view.

    def get_object(self, pk):
        try:
            return city_handler.get_by_attribute(pk=pk).first()
        except city_handler.city_repo.model.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        city = self.get_object(pk)
        return Response(model_to_dict(city), status=status.HTTP_200_OK)


class CityListView(APIView):
    # City List API view.

    def get(self, request, format=None):
        cities = city_handler.get_all()
        city_list = [model_to_dict(city) for city in cities]
        return Response(city_list)

    def post(self, request, format=None):
        if not all(attr in request.data.keys() for attr in REQUIRED_POST_REQUEST_DATA):
            return Response("Wrong request body data", status=status.HTTP_400_BAD_REQUEST)
        try:
            city_dto = CityCreateDTO(**request.data)
            city = city_handler.create(city_dto)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(model_to_dict(city), status=status.HTTP_201_CREATED)
