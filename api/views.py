import logging

import requests
from django.shortcuts import render
import pandas as pd

from api.service import fetch_geocode, get_om_response, WEATHER_CODES

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s.",
    datefmt="%Y.%m.%d %H:%M:%S",
)


def index(request):
    weather_data = None
    if request.method == "POST":
        city = request.POST.get("city")
        if city:
            lat, lon = fetch_geocode(city)
            if lat and lon:
                daily_df = get_om_response(lat, lon)
                weather_data = daily_df.to_dict(orient="records")
                print(weather_data)
                for entry in weather_data:
                    entry["date"] = entry["date"].strftime("%Y-%m-%d")
                    entry["weather_description"] = WEATHER_CODES.get(
                        int(entry["weather_code"]), "Неизвестный код"
                    )
            else:
                weather_data = {"error": "Invalid city provided"}
        else:
            weather_data = {"error": "City is not provided"}
    return render(request, "index.html", {"weather_data": weather_data})
