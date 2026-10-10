# Waldur Prometheus Exporter

This service exports [Waldur](https://waldur.com) metrics in a format compatible with [Prometheus](https://prometheus.io/). It collects statistics about users, projects, customers, resources, and usage from a Waldur Mastermind instance.

## Features

- **User Statistics**: Total users, owners, support staff, and local users.
- **Organization Statistics**: Counts of organizations, projects, and resources per organization.
- **Resource Statistics**: Active resources grouped by offering, country, and organization group.
- **Financial Statistics**: Total cost of active resources per offering.
- **Usage & Limits**: Aggregated usages and limits grouped by various dimensions (OECD, industry flag).
- **Provisioning Metrics**: Success rates, durations, and counts of provisioning attempts.
- **Matrix Chat Health**: Diagnostics check results and rooms by state.

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
  -e LOG_FORMAT=json \
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
    export LOG_FORMAT=console  # optional: readable logs for development
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
| `WALDUR_API_TOKEN` | An authentication token for the Waldur API. The Matrix chat metrics need a staff or support user's token (staff only with an older Waldur Mastermind). | Yes |
| `LOG_FORMAT` | Log output format: `json` (default) for structured JSON, `console` for readable development output. | No |

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

### Matrix chat

Read from `GET /api/admin/matrix/diagnostics/`, which only answers staff and support users, and from the room counts of `/api/matrix/rooms/`. An older Waldur Mastermind answers diagnostics for staff users only.

Use the token of a user kept for monitoring. Diagnostics runs some of its checks as the user who calls it, and signs that user in on a test device if they have a Matrix account, which opening the chat or belonging to a project with a room gives them; with a person's own token, that happens to their account on every collection.

| Metric | Labels | Description |
|--------|--------|-------------|
| `waldur_matrix_diagnostics_up` | | `1` if the last diagnostics call succeeded, `0` if it failed. |
| `waldur_matrix_check_passed` | `check` | `1` if the diagnostics check passed, `0` if it failed. One series per check the endpoint returns, e.g. `bot_running`, `bot_whoami`, `homeserver_reachable`, `appservice_ping`, `room_stats`. |
| `waldur_matrix_rooms` | `state` | Rooms per state: `active`, `archived`, `creating`, `disabling`, `error`. |

The other Matrix metrics are only published while the diagnostics call succeeds, and the room counts only while every one of them succeeds. A failure is logged as a warning when it starts or changes, not on every collection; a `403` means the token's user is not staff or support.

The endpoint answers even where Matrix chat is not set up, with its checks failing, and not every check matters on every deployment: `livekit_configured` fails wherever calls are not set up. Alert on the checks you need rather than on any `0`.

## Development

### Linting & Code Quality

This project uses `ruff` for linting and formatting, and `mypy` for type checking.

To run checks locally:

```bash
# Install pre-commit hooks (optional, runs on each commit)
uv tool install prek

# Run all checks
uvx prek run --all-files
```

### CI/CD

GitLab CI configures the pipeline to:

- Run linters (`ruff`, `mypy`) via `prek`.
- Generate SBOMs (Software Bill of Materials) on release tags and attach them to the GitHub release.
