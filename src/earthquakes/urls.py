from django.urls import path

from . import views

urlpatterns = [
    path("get_closest/", views.ClosesEarthquakeView.as_view(), name="get_closest"),
]
