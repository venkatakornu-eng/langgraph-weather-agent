from datetime import datetime, timedelta
from components.config import config


def classify_temperature(temp_celsius: float) -> str:
    """Classify a Celsius temperature into a readable comfort band."""
    if temp_celsius < config.TEMP_COLD:
        return "cold"
    if temp_celsius < config.TEMP_COOL:
        return "cool"
    if temp_celsius < config.TEMP_COMFORTABLE:
        return "comfortable"
    if temp_celsius < config.TEMP_WARM:
        return "warm"
    return "hot"


def get_weather_description(weather_code: int) -> str:
    """Translate a WMO weather code into human-readable text."""
    return config.WEATHER_CODE_DESCRIPTIONS.get(
        weather_code, f"Weather code {weather_code}"
    )


def get_greeting(is_day: int) -> str:
    """Return a simple day/night greeting."""
    return "Good day" if int(is_day) == 1 else "Good evening"


def parse_utc_offset(utc_offset_str: str) -> timedelta:
    """Parse offsets such as +0100, +01:00, -0800, or -08:00."""
    try:
        raw = (utc_offset_str or "+0000").strip()
        sign = -1 if raw.startswith("-") else 1
        digits = raw.lstrip("+-")

        if ":" in digits:
            hours, minutes = (int(value) for value in digits.split(":", 1))
        elif len(digits) == 4:
            hours, minutes = int(digits[:2]), int(digits[2:])
        else:
            hours, minutes = int(digits or "0"), 0

        return timedelta(hours=sign * hours, minutes=sign * minutes)
    except (TypeError, ValueError):
        return timedelta(0)


def normalise_utc_offset(utc_offset_str: str) -> str:
    """Return an offset in ±HH:MM form for display."""
    raw = (utc_offset_str or "+0000").strip()
    sign = "-" if raw.startswith("-") else "+"
    digits = raw.lstrip("+-").replace(":", "")
    if len(digits) == 4 and digits.isdigit():
        return f"{sign}{digits[:2]}:{digits[2:]}"
    return raw


def format_local_time(utc_time_str: str, utc_offset_str: str) -> str:
    """Convert a UTC timestamp into local display time.

    Kept for backwards compatibility and utility testing. Stage 2 weather calls now
    request the city's timezone directly from Open-Meteo and use
    ``format_weather_time`` below.
    """
    try:
        utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
        local_time = utc_time + parse_utc_offset(utc_offset_str)
        offset_display = normalise_utc_offset(utc_offset_str)
        return f"{utc_time:%H:%M} UTC | {local_time:%H:%M} (UTC{offset_display})"
    except (TypeError, ValueError):
        return "Time unavailable"


def offset_seconds_to_text(offset_seconds: int) -> str:
    """Convert an offset in seconds to a display value such as +01:00."""
    sign = "-" if offset_seconds < 0 else "+"
    total_minutes = abs(int(offset_seconds)) // 60
    hours, minutes = divmod(total_minutes, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def format_weather_time(
    local_time_str: str,
    timezone_name: str,
    utc_offset_seconds: int,
) -> str:
    """Format a local timestamp returned by Open-Meteo."""
    try:
        local_time = datetime.fromisoformat(local_time_str)
        offset_display = offset_seconds_to_text(utc_offset_seconds)
        return f"{local_time:%H:%M} local ({timezone_name}, UTC{offset_display})"
    except (TypeError, ValueError):
        return "Time unavailable"


def wind_direction_to_compass(degrees: float) -> str:
    """Convert wind direction in degrees to an 8-point compass label."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[round((degrees % 360) / 45) % 8]


def build_weather_advice(temp_celsius: float, weather_code: int, windspeed: float) -> str:
    """Generate lightweight, deterministic user advice from current conditions."""
    tips: list[str] = []

    if weather_code in {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82}:
        tips.append("Carry an umbrella or waterproof layer")
    elif weather_code in {71, 73, 75, 77, 85, 86}:
        tips.append("Allow extra travel time because of snow")
    elif weather_code in {95, 96, 99}:
        tips.append("Take care outdoors because thunderstorms are possible")

    if temp_celsius < 10:
        tips.append("Wear a warm layer")
    elif temp_celsius >= 26:
        tips.append("Stay hydrated if you will be outside")

    if windspeed >= 40:
        tips.append("Expect strong winds")

    return "; ".join(tips) if tips else "Conditions look manageable for normal activities"
