from typing import Any

import requests
from pydantic import ValidationError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from components.config import config
from components.helper_functions import (
    build_weather_advice,
    classify_temperature,
    format_weather_time,
    get_greeting,
    get_weather_description,
    wind_direction_to_compass,
)
from components.schema import GeocodingResult, LocationData, WeatherData
from components.state import WeatherAgentState


def _session_with_retries() -> requests.Session:
    """Build an HTTP session with bounded retries for transient server failures.

    HTTP 429 is deliberately not retried. A rate limit is handled by the
    location fallback flow instead of repeatedly calling the same service.
    """
    retry = Retry(
        total=config.MAX_RETRIES,
        connect=config.MAX_RETRIES,
        read=config.MAX_RETRIES,
        backoff_factor=0.4,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def choose_location_strategy(state: WeatherAgentState) -> dict[str, Any]:
    """Entry node used before LangGraph conditionally selects a location path."""
    return {}


def select_location_strategy(state: WeatherAgentState) -> str:
    """Route to manual geocoding when a city is supplied, otherwise use IP lookup."""
    requested_city = (state.get("requested_city") or "").strip()
    return "manual" if requested_city else "automatic"


def route_after_location(state: WeatherAgentState) -> str:
    """Continue to weather retrieval only when location resolution succeeded."""
    return "weather" if state.get("location_data") else "location_error"


def fetch_location_data(state: WeatherAgentState) -> dict[str, Any]:
    """Fetch and validate approximate location from the public IP address.

    Location-provider failures are returned in state instead of crashing the graph,
    allowing the CLI to offer a manual-city fallback.
    """
    try:
        with _session_with_retries() as session:
            response = session.get(config.LOCATION_API_URL, timeout=config.REQUEST_TIMEOUT)

            if response.status_code == 429:
                return {
                    "location_data": None,
                    "location_source": "automatic",
                    "location_error": (
                        "Automatic IP location is temporarily rate-limited (HTTP 429)."
                    ),
                }

            response.raise_for_status()

        payload = response.json()
        if payload.get("error"):
            raise ValueError(payload.get("reason", "Location service returned an error"))

        location = LocationData.model_validate(payload)
        return {
            "location_data": location.model_dump(),
            "location_source": "automatic",
            "location_error": None,
        }

    except requests.RequestException as exc:
        return {
            "location_data": None,
            "location_source": "automatic",
            "location_error": f"Automatic location lookup failed: {exc}",
        }
    except (ValidationError, ValueError) as exc:
        return {
            "location_data": None,
            "location_source": "automatic",
            "location_error": f"Automatic location data was invalid: {exc}",
        }


def geocode_city_data(state: WeatherAgentState) -> dict[str, Any]:
    """Resolve a user-supplied city to coordinates using Open-Meteo Geocoding."""
    requested_city = (state.get("requested_city") or "").strip()
    if len(requested_city) < 2:
        return {
            "location_data": None,
            "location_source": "manual",
            "location_error": "Please enter at least two characters for the city name.",
        }

    params = {
        "name": requested_city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        with _session_with_retries() as session:
            response = session.get(
                config.GEOCODING_API_URL,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

        payload = response.json()
        if payload.get("error"):
            raise ValueError(payload.get("reason", "Geocoding service returned an error"))

        results = payload.get("results") or []
        if not results:
            return {
                "location_data": None,
                "location_source": "manual",
                "location_error": (
                    f"No location match was found for '{requested_city}'. "
                    "Try a more specific value such as 'Hyderabad, India'."
                ),
            }

        match = GeocodingResult.model_validate(results[0])
        location = LocationData(
            city=match.name,
            region=match.admin1,
            country_name=match.country or match.country_code,
            latitude=match.latitude,
            longitude=match.longitude,
            timezone=match.timezone,
        )

        return {
            "location_data": location.model_dump(),
            "location_source": "manual",
            "location_error": None,
        }

    except requests.RequestException as exc:
        return {
            "location_data": None,
            "location_source": "manual",
            "location_error": f"City lookup failed: {exc}",
        }
    except (ValidationError, ValueError) as exc:
        return {
            "location_data": None,
            "location_source": "manual",
            "location_error": f"City lookup returned invalid data: {exc}",
        }


def fetch_weather_data(state: WeatherAgentState) -> dict[str, Any]:
    """Fetch and validate current weather for the resolved coordinates."""
    location = state.get("location_data")
    if not location:
        raise RuntimeError("Location data not available for weather fetch")

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current_weather": "true",
        # Ask Open-Meteo to return timestamps in the resolved location's timezone.
        "timezone": location.get("timezone") or "auto",
    }

    try:
        with _session_with_retries() as session:
            response = session.get(
                config.WEATHER_API_BASE_URL,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

        weather = WeatherData.model_validate(response.json())
        return {"weather_data": weather.model_dump()}

    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch weather data: {exc}") from exc
    except ValidationError as exc:
        raise RuntimeError(f"Invalid weather data received: {exc}") from exc


def generate_location_error(state: WeatherAgentState) -> dict[str, str]:
    """Generate a user-facing message when neither location route produced a match."""
    requested_city = (state.get("requested_city") or "").strip()
    detail = state.get("location_error") or "Location could not be resolved."

    if requested_city:
        message = (
            f"Unable to resolve weather for '{requested_city}'.\n"
            f"Reason: {detail}\n"
            "Try entering a more specific city, for example 'Hyderabad, India'."
        )
    else:
        message = (
            "Automatic location detection is unavailable.\n"
            f"Reason: {detail}\n"
            "Please enter a city manually to continue."
        )

    return {"weather_info": message}


def generate_weather_info(state: WeatherAgentState) -> dict[str, str]:
    """Create the final personalized weather summary."""
    location = state.get("location_data")
    weather_data = state.get("weather_data")
    if not location or not weather_data:
        raise RuntimeError("Location or weather data not available for summary generation")

    weather = weather_data["current_weather"]
    units = weather_data.get("current_weather_units", {})

    temperature = float(weather["temperature"])
    windspeed = float(weather["windspeed"])
    wind_direction = float(weather["winddirection"])
    weather_code = int(weather["weathercode"])

    location_bits = [
        location.get("city", ""),
        location.get("region", ""),
        location.get("country_name", ""),
    ]
    location_text = ", ".join(bit for bit in location_bits if bit)
    source_text = "manual city search" if state.get("location_source") == "manual" else "automatic IP detection"

    summary = [
        f"{get_greeting(weather['is_day'])}, {state['name']}!",
        f"Location: {location_text}",
        f"Location source: {source_text}",
        f"Time: {format_weather_time(weather['time'], weather_data.get('timezone', location.get('timezone', 'UTC')), weather_data.get('utc_offset_seconds', 0))}",
        "",
        "Current conditions",
        f"• Weather: {get_weather_description(weather_code)}",
        (
            f"• Temperature: {temperature:.1f}{units.get('temperature', '°C')} "
            f"({classify_temperature(temperature)})"
        ),
        (
            f"• Wind: {windspeed:.1f} {units.get('windspeed', 'km/h')} "
            f"from {wind_direction_to_compass(wind_direction)} ({wind_direction:.0f}°)"
        ),
        "",
        f"Recommendation: {build_weather_advice(temperature, weather_code, windspeed)}.",
    ]

    return {"weather_info": "\n".join(summary)}
