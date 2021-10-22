# Use to avoid pull rate limit for Docker Hub images
ARG DOCKER_REGISTRY=docker.io/
FROM ${DOCKER_REGISTRY}library/python:3.8

COPY . /usr/src/waldur-prometheus-exporter

WORKDIR /usr/src/waldur-prometheus-exporter
RUN pip install -r requirements.txt --no-cache-dir

CMD [ "python", "src/app.py" ]
