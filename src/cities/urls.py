from django.urls import path

from cities import views

urlpatterns = [
    path("create/", views.CityListView.as_view(), name="create_city"),
    path("get/<int:pk>/", views.CityDetailView.as_view(), name="get_city"),
    path("get/", views.CityListView.as_view(), name="get_cities"),
]
