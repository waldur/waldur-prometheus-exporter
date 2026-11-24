# --- Stage 1: Builder ---
ARG DOCKER_REGISTRY=docker.io/
FROM ${DOCKER_REGISTRY}astral/uv:python3.13-alpine AS builder

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
FROM ${DOCKER_REGISTRY}python:3.13-alpine

# 1. Take the Alpine security fixes released since the base image was built,
#    and create a non-root user
RUN apk upgrade --no-cache && \
    addgroup -S waldur && adduser -S waldur -G waldur

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
    