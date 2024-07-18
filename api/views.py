import json
import logging

from django.http import JsonResponse
from django.shortcuts import render

from api.service import fetch_geocode, get_om_response, WEATHER_CODES
from env_vars import Settings, get_settings

cfg: Settings = get_settings()

OWM_API_KEY = cfg.OWM_API_KEY

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s.",
    datefmt="%Y.%m.%d %H:%M:%S",
)


def index(request):
    weather_data = None
    city = None
    if request.method == "POST":
        city = request.POST.get("city")
        if city:
            city.capitalize()
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
                weather_data = {"error": "Invalid city provided", "city": city}
        else:
            city = None
            weather_data = {"error": "City is not provided", "city": None}
    return render(request, "index.html", {"weather_data": weather_data, "city": city})


def autocomplete_city(request):
    if "q" in request.GET:
        query = request.GET.get("q").lower()
        with open("api/cities.json", "r", encoding="utf-8") as f:
            cities = json.load(f)
        results = [city["name"] for city in cities if query in city["name"].lower()]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)
