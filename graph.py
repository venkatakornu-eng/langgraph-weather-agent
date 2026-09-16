from langgraph.graph import END, START, StateGraph

from components.nodes import fetch_location_data, fetch_weather_data, generate_weather_info
from components.state import WeatherAgentState


def build_weather_agent():
    """Build and compile the Weather Agent workflow."""
    builder = StateGraph(WeatherAgentState)

    builder.add_node("fetch_location_data", fetch_location_data)
    builder.add_node("fetch_weather_data", fetch_weather_data)
    builder.add_node("generate_weather_info", generate_weather_info)

    builder.add_edge(START, "fetch_location_data")
    builder.add_edge("fetch_location_data", "fetch_weather_data")
    builder.add_edge("fetch_weather_data", "generate_weather_info")
    builder.add_edge("generate_weather_info", END)

    return builder.compile()


weather_agent = build_weather_agent()
