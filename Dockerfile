FROM python:3.10-slim-bullseye AS BUILDER
LABEL maintainer="mario.bielert@tu-dresden.de"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    protobuf-compiler \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m metricq

COPY --chown=metricq:metricq . /home/metricq/metricq

WORKDIR /home/metricq/metricq

USER metricq
RUN pip install --user . 


FROM python:3.10-slim-bullseye
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libprotobuf23 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m metricq 

WORKDIR /home/metricq/

COPY --from=BUILDER --chown=metricq:metricq /home/metricq/.local /home/metricq/.local

USER metricq
