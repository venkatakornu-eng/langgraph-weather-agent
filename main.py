from graph import weather_agent


def run_weather_agent(name: str) -> dict:
    """Run the graph and return its final state."""
    initial_state = {
        "name": name.strip() or "User",
        "location_data": None,
        "weather_data": None,
        "weather_info": None,
    }
    return weather_agent.invoke(initial_state)


def main() -> None:
    """CLI entry point."""
    name = input("Enter your name: ").strip() or "User"

    try:
        final_state = run_weather_agent(name)
        print("\n" + "=" * 60)
        print("WEATHER AGENT")
        print("=" * 60)
        print(final_state.get("weather_info") or "Weather information is unavailable.")
    except Exception as exc:
        print(f"\nWeather Agent could not complete the request: {exc}")
        print("Please check your internet connection or try again shortly.")


if __name__ == "__main__":
    main()
