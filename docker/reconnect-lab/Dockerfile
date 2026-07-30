FROM python:3.11-slim-bullseye

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       protobuf-compiler \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Editable install so the container always runs the checked-out source,
# not a stale copy -- rebuild after every client-side change you want to test.
RUN pip install --no-cache-dir -e '.[examples]'
