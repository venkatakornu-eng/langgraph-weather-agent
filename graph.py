from langgraph.graph import END, START, StateGraph

from components.nodes import (
    choose_location_strategy,
    fetch_location_data,
    fetch_weather_data,
    generate_location_error,
    generate_weather_info,
    geocode_city_data,
    route_after_location,
    select_location_strategy,
)
from components.state import WeatherAgentState


def build_weather_agent():
    """Build and compile the resilient Weather Agent workflow."""
    builder = StateGraph(WeatherAgentState)

    builder.add_node("choose_location_strategy", choose_location_strategy)
    builder.add_node("fetch_location_data", fetch_location_data)
    builder.add_node("geocode_city_data", geocode_city_data)
    builder.add_node("fetch_weather_data", fetch_weather_data)
    builder.add_node("generate_location_error", generate_location_error)
    builder.add_node("generate_weather_info", generate_weather_info)

    # Stage 2: route between automatic IP lookup and manual city geocoding.
    builder.add_edge(START, "choose_location_strategy")
    builder.add_conditional_edges(
        "choose_location_strategy",
        select_location_strategy,
        {
            "automatic": "fetch_location_data",
            "manual": "geocode_city_data",
        },
    )

    # Both location strategies share the same success/failure routing rule.
    builder.add_conditional_edges(
        "fetch_location_data",
        route_after_location,
        {
            "weather": "fetch_weather_data",
            "location_error": "generate_location_error",
        },
    )
    builder.add_conditional_edges(
        "geocode_city_data",
        route_after_location,
        {
            "weather": "fetch_weather_data",
            "location_error": "generate_location_error",
        },
    )

    builder.add_edge("fetch_weather_data", "generate_weather_info")
    builder.add_edge("generate_weather_info", END)
    builder.add_edge("generate_location_error", END)

    return builder.compile()


weather_agent = build_weather_agent()
