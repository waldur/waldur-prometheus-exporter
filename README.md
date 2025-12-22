# Waldur Prometheus Exporter

This service exports [Waldur](https://waldur.com) metrics in a format compatible with [Prometheus](https://prometheus.io/). It collects statistics about users, projects, customers, resources, and usage from a Waldur Mastermind instance.

## Features

- **User Statistics**: Total users, owners, support staff, and local users.
- **Organization Statistics**: Counts of organizations, projects, and resources per organization.
- **Resource Statistics**: Active resources grouped by offering, country, and organization group.
- **Financial Statistics**: Total cost of active resources per offering.
- **Usage & Limits**: Aggregated usages and limits grouped by various dimensions (OECD, industry flag).
- **Provisioning Metrics**: Success rates, durations, and counts of provisioning attempts.

## Prerequisites

- Python 3.11+
- Access to a Waldur Mastermind API

## Installation & Running

### Using Docker (Recommended)

Artifacts are built using a multistage Dockerfile.

```bash
docker build -t waldur-prometheus-exporter .
docker run -d \
  -p 8080:8080 \
  -e WALDUR_API_URL="https://waldur.example.com/api" \
  -e WALDUR_API_TOKEN="your-waldur-api-token" \
  waldur-prometheus-exporter
```

### Local Development

This project uses [`uv`](https://github.com/astral-sh/uv) for dependency management.

1. **Clone the repository:**

    ```bash
    git clone git@github.com:waldur/waldur-prometheus-exporter.git
    cd waldur-prometheus-exporter
    ```

2. **Install dependencies:**

    ```bash
    uv sync
    ```

3. **Set environment variables:**

    ```bash
    export WALDUR_API_URL="https://waldur.example.com/api"
    export WALDUR_API_TOKEN="your-waldur-api-token"
    ```

4. **Run the exporter:**

    ```bash
    # Activate virtual environment
    source .venv/bin/activate
    
    # Run application
    python src/app.py
    ```

    The metrics will be available at `http://localhost:8080/metrics`.

## Configuration

The application is configured via environment variables.

| Variable | Description | Required |
|----------|-------------|----------|
| `WALDUR_API_URL` | The URL of the Waldur Mastermind API (e.g., `https://waldur.example.com/api`). | Yes |
| `WALDUR_API_TOKEN` | An authentication token for the Waldur API. | Yes |

- **Port**: The exporter listens on port `8080`.
- **Collection Interval**: Metrics are collected every 120 seconds.

## Metrics

The exporter exposes metrics with the `waldur_` prefix. Some key metrics include:

- `waldur_users_total`: Total count of users.
- `waldur_customers_total`: Total count of organizations.
- `waldur_projects_total`: Total count of projects.
- `waldur_marketplace_resources_total`: Total count of active resources.
- `waldur_total_cost_of_active_resources_per_offering`: Cost metrics.
- `waldur_provisioning_success_rate`: Provisioning reliability metrics.

## Development

### Linting & Code Quality

This project uses `ruff` for linting and formatting, and `mypy` for type checking.

To run checks locally:

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run all checks
uv run pre-commit run --all
```

### CI/CD

GitLab CI configures the pipeline to:

- Run linters (`ruff`, `mypy`) via `pre-commit`.
- Generate SBOMs (Software Bill of Materials).
