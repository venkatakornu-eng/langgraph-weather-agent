from graph import weather_agent


def run_weather_agent(name: str, requested_city: str | None = None) -> dict:
    """Run the graph and return its final state."""
    initial_state = {
        "name": name.strip() or "User",
        "requested_city": (requested_city or "").strip() or None,
        "location_source": None,
        "location_error": None,
        "location_data": None,
        "weather_data": None,
        "weather_info": None,
    }
    return weather_agent.invoke(initial_state)


def _print_result(final_state: dict) -> None:
    print("\n" + "=" * 60)
    print("WEATHER AGENT")
    print("=" * 60)
    print(final_state.get("weather_info") or "Weather information is unavailable.")


def main() -> None:
    """CLI entry point with automatic-location fallback to manual city search."""
    name = input("Enter your name: ").strip() or "User"
    requested_city = input(
        "Enter city (leave blank for automatic location detection): "
    ).strip()

    try:
        final_state = run_weather_agent(name, requested_city or None)

        # If automatic IP lookup fails (for example HTTP 429), offer manual input
        # instead of terminating the application.
        if not requested_city and final_state.get("location_error"):
            print("\nAutomatic location detection is temporarily unavailable.")
            print(f"Reason: {final_state['location_error']}")
            fallback_city = input("Enter your city manually: ").strip()

            if fallback_city:
                final_state = run_weather_agent(name, fallback_city)
            else:
                print("No city was entered. Weather lookup cancelled.")
                return

        _print_result(final_state)

    except Exception as exc:
        print(f"\nWeather Agent could not complete the request: {exc}")
        print("Please check your internet connection or try again shortly.")


if __name__ == "__main__":
    main()
