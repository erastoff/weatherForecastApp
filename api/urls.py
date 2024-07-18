from django.urls import path

from api.views import index

app_name = "api"

urlpatterns = [
    path(
        "",
        index,
        name="index",
    ),
]
