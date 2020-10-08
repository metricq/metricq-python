![BSD 3-clause](https://img.shields.io/badge/license-BSD%203--clause-blue.svg)
![Python package](https://github.com/metricq/metricq-python/workflows/Python%20package/badge.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![PyPI](https://img.shields.io/pypi/v/metricq)](https://pypi.org/project/metricq/)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/metricq)
[![Docker pulls](https://img.shields.io/docker/pulls/metricq/metricq-python.svg)](https://hub.docker.com/r/metricq/metricq-python)

# metricq - python libraries

This is a python implementation of the MetricQ protocol.
It allows you to write Sources and Sinks to easily send and receive data over
the MetricQ infrastructure.

## Installation

Install the package from PyPI:

```sh
$ pip install metricq
```

## Examples

The [`examples`](/tree/master/examples/) directory contains some basic
examples.
To play around with them, check out a copy of this repository and (in your
favourite venv) install their dependencies:

```sh
$ pip install -e '.[examples]'
```

A simple Source is implemented in `metricq_source.py`, as is a Sink in `metricq_sink.py`.
We will use the former to produce data for a metric called `test.py.dummy`, which we
will then receive and print with the latter.

Assuming a MetricQ instance is reachable at `localhost`, configure a
client<sup>(consult the documentation of your favourite config provider on how
to do that)</sup> named `source-py-dummy` to produce values with a frequence of
0.5Hz (i.e. every 2 seconds) :

```json
{
    "rate": 0.5
}
```

To start the Source, run:

```sh
$ ./examples/metricq_source.py --server 'amqp://localhost/' --token 'source-py-dummy'
```

This should now send values for the metric `test.py.dummy` in 2-second intervals.
To see (in detail) what's going on, add `-v DEBUG` to the arguments above.

On the other side, run

```sh
$ ./examples/metricq_sink.py --server 'amqp://localhost/' --metrics 'test.py.dummy'
```

and you should see new values for the metric `test.py.dummy` appear ever 2 seconds.

## Development setup

Clone the repository, and in a virtual environment run

```sh
$ pip install -e '.[dev]'
```

This will install all tools necessary for testing and linting.
To test code manually, run `pytest`.
Format code using `black` and `isort`, or lint with `flake8`.
To make sure a source distribution (`sdist`) contains the correct files, run `check-manifest`.
Tools are configured in `setup.cfg` respectively `pyproject.toml`.

To test code in a fresh environment, run the `tox` test harness:

```sh
$ tox
```

This runs the same step as our CI does.
If `tox` passes locally there's high chances that CI steps will pass too.

We recommend to install our [pre-commit](https://pre-commit.com) hooks:

```sh
$ pre-commit install
```

This way commits that fail tests or do not comply with our code style are rejected right away.
