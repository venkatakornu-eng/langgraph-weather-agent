# LangGraph Weather Agent

A small agentic Python application that detects the user's approximate location from their public IP address, retrieves live weather from Open-Meteo, validates API responses with Pydantic, and generates a personalized weather summary through a LangGraph state workflow.

## Workflow

`START -> fetch_location_data -> fetch_weather_data -> generate_weather_info -> END`

## Improvements completed

- Restored the missing weather-fetch graph edge.
- Compiled the LangGraph correctly before invocation.
- Fixed the blank weather API URL.
- Fixed temperature classification logic.
- Preserved and validated the location API response instead of replacing it with `{}`.
- Corrected the `country_name` field mismatch.
- Corrected the Python `__main__` entry point.
- Added HTTP retries and clearer error handling.
- Added Pydantic validation for external API payloads.
- Added wind direction formatting and deterministic weather recommendations.
- Added unit tests for core logic and output generation.
- Corrected the requirements file encoding/dependencies.

## Setup

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
weather_agent_final/
├── components/
│   ├── __init__.py
│   ├── config.py
│   ├── helper_functions.py
│   ├── nodes.py
│   ├── schema.py
│   └── state.py
├── tests/
│   ├── test_helper_functions.py
│   └── test_nodes.py
├── .env.example
├── graph.py
├── main.py
├── requirements.txt
└── README.md
```
