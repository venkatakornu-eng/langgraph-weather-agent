import unittest
from unittest.mock import MagicMock, patch

from components.nodes import (
    fetch_location_data,
    generate_location_error,
    generate_weather_info,
    geocode_city_data,
    route_after_location,
    select_location_strategy,
)


class RoutingTests(unittest.TestCase):
    def test_location_strategy(self):
        self.assertEqual(select_location_strategy({"requested_city": None}), "automatic")
        self.assertEqual(select_location_strategy({"requested_city": "Hyderabad"}), "manual")

    def test_route_after_location(self):
        self.assertEqual(route_after_location({"location_data": {"city": "Leicester"}}), "weather")
        self.assertEqual(route_after_location({"location_data": None}), "location_error")


class LocationNodeTests(unittest.TestCase):
    @patch("components.nodes._session_with_retries")
    def test_ip_rate_limit_becomes_fallback_state(self, mock_session_factory):
        response = MagicMock()
        response.status_code = 429

        session = MagicMock()
        session.get.return_value = response
        mock_session_factory.return_value.__enter__.return_value = session

        result = fetch_location_data({})
        self.assertIsNone(result["location_data"])
        self.assertEqual(result["location_source"], "automatic")
        self.assertIn("429", result["location_error"])

    @patch("components.nodes._session_with_retries")
    def test_manual_city_geocoding(self, mock_session_factory):
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "results": [
                {
                    "name": "Hyderabad",
                    "latitude": 17.38405,
                    "longitude": 78.45636,
                    "timezone": "Asia/Kolkata",
                    "country": "India",
                    "country_code": "IN",
                    "admin1": "Telangana",
                }
            ]
        }

        session = MagicMock()
        session.get.return_value = response
        mock_session_factory.return_value.__enter__.return_value = session

        result = geocode_city_data({"requested_city": "Hyderabad"})
        self.assertIsNone(result["location_error"])
        self.assertEqual(result["location_source"], "manual")
        self.assertEqual(result["location_data"]["city"], "Hyderabad")
        self.assertEqual(result["location_data"]["region"], "Telangana")
        self.assertEqual(result["location_data"]["timezone"], "Asia/Kolkata")

    def test_location_error_message(self):
        result = generate_location_error(
            {
                "requested_city": "Unknown Place",
                "location_error": "No match found",
            }
        )
        self.assertIn("Unknown Place", result["weather_info"])
        self.assertIn("more specific city", result["weather_info"])


class GenerateWeatherInfoTests(unittest.TestCase):
    def test_summary_generation(self):
        state = {
            "name": "Alex",
            "requested_city": "Leicester",
            "location_source": "manual",
            "location_error": None,
            "location_data": {
                "city": "Leicester",
                "region": "England",
                "country_name": "United Kingdom",
                "latitude": 52.6369,
                "longitude": -1.1398,
                "utc_offset": "+0100",
                "timezone": "Europe/London",
            },
            "weather_data": {
                "timezone": "Europe/London",
                "utc_offset_seconds": 3600,
                "current_weather": {
                    "time": "2026-09-16T17:45",
                    "temperature": 17.5,
                    "windspeed": 12.0,
                    "winddirection": 225,
                    "is_day": 1,
                    "weathercode": 2,
                },
                "current_weather_units": {
                    "temperature": "°C",
                    "windspeed": "km/h",
                },
            },
            "weather_info": None,
        }

        result = generate_weather_info(state)
        text = result["weather_info"]
        self.assertIn("Alex", text)
        self.assertIn("Leicester", text)
        self.assertIn("manual city search", text)
        self.assertIn("17:45 local", text)
        self.assertIn("Partly cloudy", text)
        self.assertIn("cool", text)
        self.assertIn("SW", text)


if __name__ == "__main__":
    unittest.main()
