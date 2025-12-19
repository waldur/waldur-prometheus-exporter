# --- Stage 1: Builder ---
ARG DOCKER_REGISTRY=docker.io/
FROM ${DOCKER_REGISTRY}astral/uv:python3.11-alpine AS builder

# Install build-time dependencies
RUN apk add --no-cache git

# Set up project location
WORKDIR /usr/src/waldur-prometheus-exporter

# Copy only the files needed for dependency resolution to improve caching
COPY pyproject.toml uv.lock ./

# Install dependencies (creates .venv)
# --frozen: ensures uv.lock is not updated
# --no-install-project: skip installing the project itself in this layer
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the source code and sync again to install the project
COPY . .
RUN uv sync --frozen --no-dev


# --- Stage 2: Runtime ---
FROM ${DOCKER_REGISTRY}python:3.11-alpine

# 1. Create a non-root user
RUN addgroup -S waldur && adduser -S waldur -G waldur

# 2. Set up working directory
WORKDIR /usr/src/waldur-prometheus-exporter

# 3. Copy the virtual environment and source code from the builder
# We only copy the .venv (which contains all dependencies) and your src
COPY --from=builder --chown=waldur:waldur /usr/src/waldur-prometheus-exporter/.venv ./.venv
COPY --from=builder --chown=waldur:waldur /usr/src/waldur-prometheus-exporter/src ./src

# 4. Set environment variables
# - Add the virtualenv's bin to PATH so we can call 'python' directly
# - Ensure python doesn't buffer logs
ENV PATH="/usr/src/waldur-prometheus-exporter/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

    # 5. Switch to non-root user
    USER waldur

    # 6. Run the application
    # We use the python binary inside the venv (via the updated PATH)
    CMD [ "python", "src/app.py" ]
    