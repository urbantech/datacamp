# Langflow Integration

This directory contains Langflow configurations and example flows for the scraping project.

## Directory Structure

```
flows/
├── configs/          # Langflow configuration files
├── examples/         # Example flow definitions
├── custom_components/# Custom component definitions (future)
├── data/            # Database and cached data
└── logs/            # Langflow log files
```

## Getting Started

1. Install dependencies:
```bash
poetry install
```

2. Start Langflow:
```bash
poetry run langflow --config flows/configs/langflow.yaml
```

3. Access the UI:
Open http://localhost:7860 in your browser

## Example Flows

- `test_scraper.json`: Basic flow demonstrating scraper and bot defense integration

## Configuration

The default configuration in `configs/langflow.yaml` sets up:
- Web interface on port 7860
- SQLite database for flow storage
- Memory cache for better performance
- Logging to flows/logs/langflow.log

## Custom Components

Custom components can be added to the `custom_components` directory. Each component should follow the Langflow component specification.
