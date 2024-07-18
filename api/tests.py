from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from api.views import fetch_geocode
import pandas as pd


class WeatherAppTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("api:index")

    def test_index_page_get(self):
        print(self.url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    @patch("api.views.fetch_geocode")
    @patch("api.views.get_om_response")
    def test_index_page_post_valid_city(self, mock_get_om_response, mock_fetch_geocode):
        mock_fetch_geocode.return_value = (40.7128, -74.0060)
        mock_get_om_response.return_value = pd.DataFrame(
            [
                {
                    "date": pd.Timestamp("2024-07-16 21:00:00+0000", tz="UTC"),
                    "temperature_2m_max": 30,
                    "temperature_2m_min": 19,
                    "precipitation_probability_mean": 1,
                    "rain_sum": 0.0,
                    "wind_speed_10m_max": 6,
                    "weather_code": 3,
                }
            ]
        )

        response = self.client.post(self.url, {"city": "New York"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("weather_data", response.context)
        self.assertEqual(
            response.context["weather_data"][0]["weather_description"], "Пасмурно"
        )

    @patch("api.views.fetch_geocode")
    def test_index_page_post_invalid_city(self, mock_fetch_geocode):
        mock_fetch_geocode.return_value = (None, None)
        response = self.client.post(self.url, {"city": "InvalidCity"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("weather_data", response.context)
        self.assertIn("error", response.context["weather_data"])

    def test_fetch_geocode_valid_city(self):
        with patch("api.views.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [
                {"lat": 40.7128, "lon": -74.0060}
            ]
            lat, lon = fetch_geocode("New York")
            self.assertEqual(lat, 40.7128)
            self.assertEqual(lon, -74.0060)

    def test_fetch_geocode_invalid_city(self):
        with patch("api.views.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []
            lat, lon = fetch_geocode("InvalidCity")
            self.assertIsNone(lat)
            self.assertIsNone(lon)
