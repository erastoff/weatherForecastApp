import logging

import numpy
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from env_vars import Settings, get_settings

cfg: Settings = get_settings()

OWM_API_KEY = cfg.OWM_API_KEY
OM_API = "https://api.open-meteo.com/v1/forecast"
BASE_PARAMS = {
    "timezone": "Europe/Moscow",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_mean",
        "rain_sum",
        "wind_speed_10m_max",
        "weather_code",
    ],
}

WEATHER_CODES = {
    0: "Ясное небо",
    1: "В основном ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман и изморозь",
    48: "Туман и изморозь",
    51: "Морось: Легкая интенсивность",
    53: "Морось: Умеренная интенсивность",
    55: "Морось: Сильная интенсивность",
    56: "Переохлажденная морось: Легкая интенсивность",
    57: "Переохлажденная морось: Сильная интенсивность",
    61: "Дождь: Слабая интенсивность",
    63: "Дождь: Умеренная интенсивность",
    65: "Дождь: Сильная интенсивность",
    66: "Переохлажденный дождь: Легкая интенсивность",
    67: "Переохлажденный дождь: Сильная интенсивность",
    71: "Снегопад: Слабая интенсивность",
    73: "Снегопад: Умеренная интенсивность",
    75: "Снегопад: Сильная интенсивность",
    77: "Снежные зерна",
    80: "Ливни: Слабая интенсивность",
    81: "Ливни: Умеренная интенсивность",
    82: "Ливни: Сильная интенсивность",
    85: "Снежные ливни: Слабая интенсивность",
    86: "Снежные ливни: Сильная интенсивность",
    95: "Гроза: Слабая или умеренная",
    96: "Гроза с градом: Слабая интенсивность",
    99: "Гроза с градом: Сильная интенсивность",
}


def fetch_geocode(city):
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={OWM_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200 and len(response.json()) > 0:
        data = response.json()[0]
        lat = data["lat"]
        lon = data["lon"]
        logging.info(f"API geocode results: {lat}, {lon}")
        return lat, lon
    else:
        return None, None


def fetch_om_session():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)


def get_om_response(lat, lon):
    openmeteo = fetch_om_session()
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    lon_lat = {
        "latitude": lat,
        "longitude": lon,
    }
    params = lon_lat | BASE_PARAMS
    responses = openmeteo.weather_api(OM_API, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_precipitation_probability_mean = daily.Variables(2).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
    daily_weather_code = daily.Variables(5).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        ),
        "temperature_2m_max": daily_temperature_2m_max,
        "temperature_2m_min": daily_temperature_2m_min,
        "precipitation_probability_mean": daily_precipitation_probability_mean,
        "rain_sum": daily_rain_sum,
        "wind_speed_10m_max": daily_wind_speed_10m_max,
        "weather_code": daily_weather_code,
    }

    daily_dataframe = (
        pd.DataFrame(data=daily_data)
        .astype(
            {
                "temperature_2m_max": int,
                "temperature_2m_min": int,
                "precipitation_probability_mean": int,
                "rain_sum": float,
                "wind_speed_10m_max": int,
            }
        )
        .round(
            {
                "rain_sum": 1,
            }
        )
    )
    # print(daily_dataframe)
    print(
        daily_dataframe[
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_mean",
            ]
        ]
    )
    return daily_dataframe


def main():
    get_om_response(-69.119270, -63.658104)


if __name__ == "__main__":
    main()
