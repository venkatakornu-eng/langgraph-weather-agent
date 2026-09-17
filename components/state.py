from typing import Any, Dict, Optional, TypedDict


class WeatherAgentState(TypedDict):
    """Shared state passed between LangGraph nodes."""

    # User input
    name: str
    requested_city: Optional[str]

    # Location workflow
    location_source: Optional[str]
    location_error: Optional[str]
    location_data: Optional[Dict[str, Any]]

    # Weather workflow
    weather_data: Optional[Dict[str, Any]]
    weather_info: Optional[str]
