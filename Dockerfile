FROM python:3.9-slim AS builder
LABEL maintainer="mario.bielert@tu-dresden.de"

RUN apt-get update && apt-get install -y protobuf-compiler build-essential

COPY . /metricq

WORKDIR /metricq
RUN pip install .

FROM python:3-slim
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
CMD [ "python" ]
