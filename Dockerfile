# Use to avoid pull rate limit for Docker Hub images
ARG DOCKER_REGISTRY=docker.io/
FROM ${DOCKER_REGISTRY}ghcr.io/astral-sh/uv:python3.11-alpine

COPY . /usr/src/waldur-prometheus-exporter

WORKDIR /usr/src/waldur-prometheus-exporter
RUN apk add --no-cache git
RUN uv sync --frozen

CMD [ "uv", "run", "src/app.py" ]
