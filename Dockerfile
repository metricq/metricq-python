FROM python:3.10-slim AS builder
LABEL maintainer="mario.bielert@tu-dresden.de"

RUN useradd -m metricq
RUN pip install virtualenv
RUN apt-get update && apt-get install -y protobuf-compiler build-essential

USER metricq
COPY --chown=metricq:metricq . /home/metricq/metricq

WORKDIR /home/metricq
RUN virtualenv venv

WORKDIR /home/metricq/metricq
RUN . /home/metricq/venv/bin/activate && pip install .

FROM python:3.10-slim
RUN useradd -m metricq
USER metricq
COPY --from=builder --chown=metricq:metricq /home/metricq/venv /home/metricq/venv
CMD [ "/home/metricq/venv/bin/python" ]
