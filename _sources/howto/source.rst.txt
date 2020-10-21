.. py:currentmodule:: metricq

.. _source-how-to:

Building a MetricQ Source
=========================

:term:`Sources<Source>` provide data points for a set of :term:`Metrics<Metric>` to the MetricQ network.
Usually, they are programs that continually measure some kind of quantity, for example:

- system monitoring (such as `metricq-source-sysinfo`_): CPU usage, memory utilization...
- low-level server sensor readings (e.g. via IPMI and `metricq-source-ipmi`_)
- pulling information from building automation (`metricq-source-bacnet`_)

.. _metricq-source-sysinfo: https://github.com/metricq/metricq-source-sysinfo
.. _metricq-source-ipmi: https://github.com/metricq/metricq-source-ipmi
.. _metricq-source-bacnet: https://github.com/metricq/metricq-source-bacnet

Here, we will build a simple Source that sends a random value between 0 and 1 at a configurable interval.

Defining a new Source: using :class:`metricq.Source`
----------------------------------------------------

Similarly to Sinks, we create a new Source by subclassing :class:`metricq.Source`:

.. code-block:: python

    import metricq

    class DummySource(metricq.Source):
        pass

The Source will receive its configuration dynamically over the network.
It is saved in a `JSON` format and can be entered and saved using a configuration frontend
such as the `MetricQ Wizard <https://github.com/metricq/metricq-wizard-frontend>`_.
For our purposes it's quite minimal, it only includes the rate at which to send values (in `Hz`):

.. literalinclude:: ./sink-py-dummy.config.json

This is different from the Sink we built in :ref:`sink-how-to`;
we won't pass the update rate on the command line,
instead we install a callback that is triggered every time a new configuration is received:

.. code-block:: python

    import metricq

    class DummySource(metricq.Source):
        def __init__(self, *args, **kwargs):
            # This will be set to the number of values we want to send per second:
            self._rate = None
            super().__init__(*args, **kwargs)

        @metricq.rpc_handler("config")
        async def _on_config(self, **config):
            print(f"Received new configuration: {config}")
            self._rate = config["rate"]

Clients on the MetricQ network communicate via an `RPC protocol <https://metricq.github.io/metricq-rpc-docs/>`_.
The :func:`metricq.rpc_handler` decorator is a way to define a new handler for an RPC;
here we tell the library to call :code:`_on_config` every time another client sends a :literal:`"config"`-RPC
containing our new configuration.

So far out Source would work, but it wouldn't do anything useful at all.
To change that, we first declare for which metric we want to send values,
including some helpful :ref:`metadata<metric-metadata>`:

.. code-block:: python

    import metricq

    class DummySource(metricq.Source):
        ... # as above

        @metricq.rpc_handler("config")
        async def _on_config(self, **config):
            print(f"Received new configuration: {config}")
            self._rate = config["rate"]

            metadata = {
                "rate": rate,
                "description": "A simple dummy metric providing random values, sent from a python DummySource",
            }

            await self.declare_metrics({"example.py.dummy": metadata})

To finally send some values, we override :meth:`Source.task`.
This method gets called once our Source is connected and received its initial configuration:

.. code-block:: python

    import metricq
    import asyncio
    import random

    class DummySource(metricq.Source):
        ... # as above

        async def task(self):
            while True:
                await self.send(
                    "example.py.dummy",
                    time=metricq.Timestamp.now(),
                    value=random.random(),
                )
                # Convert from rate (in Hz) to duration between sends (in seconds)
                await asyncio.sleep(1 / self._rate)

Improving constant-rate sources: using :class:`IntervalSource`
--------------------------------------------------------------

The above situation where we send values at a fixed rate is so common
that we can use the convenience class :class:`IntervalSource`, which
does all the heavy lifting for us.

Note:
    We strongly recommend implementing a :class:`IntervalSource` over a plain :class:`Source` if possible.
    It tries to automatically compensate some timing-related issues
    that inevitably arise in more complicated setups.
    See the documentation for :class:`IntervalSource` for more information.

To adapt the above example, we simply set :class:`IntervalSource.period` to the period of time between consecutive updates and replace :class:`Source.task` with :class:`IntervalSource.update`,
which gets called at a constant rate:


.. code-block:: python

    import metricq
    import asyncio
    import random

    class DummySource(metricq.Source):

        @metricq.rpc_handler("config")
        async def _on_config(self, **config):
            # Set the update period
            rate = config["rate"]
            self.period = 1 / rate

            ...

            await self.declare_metrics({"test.py.interval-dummy": metadata})


        async def update(self):
            await self.send(
                "example.py.interval-dummy",
                time=metricq.Timestamp.now(),
                value=random.random(),
            )

Running a Source
----------------

:ref:`Similarly to Sinks<sink-how-to-run>`, a Source is started by calling :meth:`run<Client.run>`.
On construction, we need to supply a unique :term:`Token` for identification and a URL of the network.

.. code-block:: python

    class DummySource(metricq.Source):

        ... # as above

    if __name__ == "__main__":
        source = DummySource(
            token="sink-py-example",
            management_url="amqp://localhost/",
        )
        source.run()


Complete Example
----------------

To obtain the dependencies required for this example, install the ``examples``-extra from the `git repo <metricq-python>`_:

.. _metricq-python: https://github.com/metricq/metricq-python

.. code-block:: shell

    $ pip install '.[examples]'

and run it like so:

.. code-block:: shell

    $ ./examples/metricq_source.py

----

.. literalinclude:: /../examples/metricq_source.py
