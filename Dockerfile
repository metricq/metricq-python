FROM python:3.10-slim-bullseye AS BUILDER
LABEL maintainer="mario.bielert@tu-dresden.de"

RUN useradd -m metricq
RUN apt-get update && apt-get install -y protobuf-compiler build-essential

COPY --chown=metricq:metricq . /home/metricq/metricq

WORKDIR /home/metricq/metricq
RUN pip install . 


FROM python:3.10-slim-bullseye
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libprotobuf23 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m metricq 

COPY --from=BUILDER /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

USER metricq
