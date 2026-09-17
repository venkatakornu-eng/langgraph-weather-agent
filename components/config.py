from typing import ClassVar, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Runtime configuration for the Weather Agent."""

    # External services
    LOCATION_API_URL: str = "https://ipapi.co/json/"
    GEOCODING_API_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"

    # Networking
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3

    # Temperature classification thresholds (Celsius)
    TEMP_COLD: float = 10.0
    TEMP_COOL: float = 18.0
    TEMP_COMFORTABLE: float = 26.0
    TEMP_WARM: float = 32.0

    # WMO weather interpretation codes used by Open-Meteo
    WEATHER_CODE_DESCRIPTIONS: ClassVar[Dict[int, str]] = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


config = Config()
