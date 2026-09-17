from pydantic import BaseModel, ConfigDict, Field


class LocationData(BaseModel):
    """Normalised location used internally by the Weather Agent."""

    model_config = ConfigDict(extra="ignore")

    city: str
    region: str = ""
    country_name: str
    latitude: float
    longitude: float
    timezone: str = "UTC"
    utc_offset: str = "+0000"


class GeocodingResult(BaseModel):
    """A location result returned by the Open-Meteo Geocoding API."""

    model_config = ConfigDict(extra="ignore")

    name: str
    latitude: float
    longitude: float
    timezone: str = "UTC"
    country: str = ""
    country_code: str = ""
    admin1: str = ""


class CurrentWeatherUnits(BaseModel):
    """Units accompanying current weather values."""

    model_config = ConfigDict(extra="ignore")

    time: str = "iso8601"
    interval: str | None = None
    temperature: str = "°C"
    windspeed: str = "km/h"
    winddirection: str = "°"
    is_day: str | None = None
    weathercode: str = "wmo code"


class CurrentWeather(BaseModel):
    """Current weather conditions from Open-Meteo."""

    model_config = ConfigDict(extra="ignore")

    time: str
    interval: int | None = None
    temperature: float
    windspeed: float
    winddirection: float
    is_day: int
    weathercode: int


class WeatherData(BaseModel):
    """Validated Open-Meteo current-weather response."""

    model_config = ConfigDict(extra="ignore")

    latitude: float
    longitude: float
    generationtime_ms: float | None = None
    utc_offset_seconds: int = 0
    timezone: str = "GMT"
    timezone_abbreviation: str | None = None
    elevation: float | None = None
    current_weather_units: CurrentWeatherUnits = Field(default_factory=CurrentWeatherUnits)
    current_weather: CurrentWeather
