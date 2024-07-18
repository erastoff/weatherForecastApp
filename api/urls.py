from django.urls import path

from api.views import index, autocomplete_city

app_name = "api"

urlpatterns = [
    path(
        "",
        index,
        name="index",
    ),
    path("autocomplete/", autocomplete_city, name="autocomplete_city"),
]
