.. _sink-how-to:

.. py:currentmodule:: metricq

Building a MetricQ Sink
=======================

:term:`Sinks<Sink>` allow you to receive and process data points for :term:`Metrics<Metric>` provided by others on the MetricQ network.
Examples of Sinks are:

- data visualization software
- database clients (such as `metricq-db-hta`_): store metric data to persistent storage
- monitoring clients
- ...

.. _metricq-db-hta: https://github.com/metricq/metricq-db-hta

Here, we will build a simple Sink that prints data points for a given list of metrics as they arrive.
You can find the complete example at `the end of this page`_ or `here <https://github.com/metricq/metricq-python/blob/master/examples/metricq_sink.py>`_.

Defining a new Sink: using :class:`metricq.Sink`
------------------------------------------------

New Sinks are defined by subclassing :class:`metricq.Sink`:

.. code-block:: python

    import metricq

    class DummySink(metricq.Sink):
        pass

We add a constructor to provide the Sink with a list of names of metrics which we are interested in printing.
All other arguments will be forwarded to the superclass:

.. code-block:: python

    import metricq

    class DummySink(metricq.Sink):
        def __init__(self, metrics: list[str], *args, **kwargs):
            self._metrics = metrics
            super().__init__(*args, **kwargs)


Now we will implement the interface needed to connect to the MetricQ network and receive metrics.
First, we tell our Sink how to connect (:meth:`metricq.Sink.connect`) to the MetricQ network.
After a connection has been established, we subscribe (:meth:`metricq.Sink.subscribe`) to the metrics we are interested in.

.. code-block:: python

    import metricq

    class DummySink(metricq.Sink):

        ... # as above

        async def connect(self):
            await super().connect()
            await self.subscribe(self._metrics)

Our Sink now needs to know what to do with the data points it receives.
We provide :meth:`Sink.on_data`, which gets called every time a new data point arrives, and tell it to print that to the standard output:

.. code-block:: python

    import metricq

    class DummySink(metricq.Sink):

        ... # as above

        async def on_data(
            self,
            metric: str,
            timestamp: metricq.Timestamp,
            value: float
        ):
            print("{}: {} {}".format(metric, timestamp, value))

Here, ``metric`` is the name of the metric for which a new data point arrived; ``value`` holds the numeric value this metric had at time indicated by ``timestamp``.


.. _sink-how-to-run:

Running a Sink
--------------

:class:`metricq.Sink` is designed as an asynchronous callback-based interface, so we won't be calling the above methods directly.
Instead, it provides :meth:`Client.run`, which handles establishing a connection, keeps track track of all the details of the MetricQ protocol and calls :meth:`Sink.on_data` once new data points arrive.

Our Sink is identified on the network by a :term:`Token`.
In general you should make sure that no two different instances of the same :term:`Client` share the same token.
Though you won't need to worry about this it if you are using :class:`metricq.Sink`,
as there is code in place that generates a unique token automatically
(see the :literal:`add_uuid` argument to :class:`metricq.Sink`).

If you are interested in the values of metric ``test.py.dummy``, construct and run ``DummySink`` as follows (assuming a MetricQ network is running on ``localhost``):

.. code-block:: python

    import metricq

    class DummySink(metricq.Sink):
        ... # as above

    if __name__ == "__main__":
        sink = DummySink(
            metrics=["test.py.dummy"],
            token="sink-py-dummy",
            management_url="amqp://localhost/"
        )
        sink.run()


This is it, assuming there is a :term:`Source` on the network that provides data points for ``test.py.dummy``.
Running this script, you should now see something like this appearing on standard output::

    ...
    test.py.dummy: [1588509320269324000] 2020-05-03 14:35:20.269324+02:00, 0.48311378740654076
    test.py.dummy: [1588509321269232000] 2020-05-03 14:35:21.269232+02:00, 0.1490083450372932
    test.py.dummy: [1588509322269017000] 2020-05-03 14:35:22.269017+02:00, 0.06578061778873023
    test.py.dummy: [1588509323267878000] 2020-05-03 14:35:23.267878+02:00, 0.7771949055949513
    test.py.dummy: [1588509324267969000] 2020-05-03 14:35:24.267969+02:00, 0.9975132302199418
    ...

See :ref:`source-how-to` on how to set up such a source.

.. _the end of this page:

Complete example
----------------

To obtain the dependencies required for this example, install the ``examples``-extra from the `git repo <metricq-python>`_:

.. _metricq-python: https://github.com/metricq/metricq-python

.. code-block:: shell

    $ pip install '.[examples]'

and run it like so:

.. code-block:: shell

    $ ./metricq_sink.py -m test.py.dummy

----

.. literalinclude:: /../examples/metricq_sink.py

Durable / persistent sinks
--------------------------

Most sinks are transient and not unique and do not have a configuration.
To create persistent sink with a configuration, subclass :class:`metricq.DurableSink` instead of :class:`metricq.Sink`.
Further, you need to implement an RPC handler for `config`.

.. code-block:: python

        @metricq.rpc_handler("config")
        async def _on_config(self, **config: Any):
            ...
