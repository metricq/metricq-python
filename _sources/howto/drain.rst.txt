.. _drain-how-to:

.. highlight:: python
.. py:currentmodule:: metricq

Building a MetricQ Drain
========================

What is a Drain?
----------------

A :class:`Drain` is a special case of a MetricQ :class:`Sink`. Both are used to 
collect the live metric data stream from MetricQ. In contrast to a :class:`Sink`,
which is continously connected to MetricQ, a :class:`Drain` is only shartly
connected to MetricQ. In particular, after the inital connection, all wanted
metrics are subscribed and the connection is closed. While the connection is 
closed, MetricQ buffers the subscribed metric data and the client can perform other 
task without any perturbation caused by the connection. Once the metric is required,
a new connection gets established and the buffered data can be received and 
processed like in a normal sink.

This bahavior is particular useful for measurements, where it is important to
reduce perturbation as much as possible.


Subscribe to metrics
--------------------

The easiest way to implement this approach is to use the classes :class:`Subscriber`
and :class:`Drain` provided by MetricQ.

In particular, the first connection is handled by the :class:`Subscriber`.

Given a server and a list of metrics, we want to subscribe to:

.. code-block::

    server: str = "amqps://user:pass@metricq.example.org/"
    metrics: List[str] = [
        # ... 
    ]

We can use the subscriber to perform the initial connect and post the subscription.
For that, we use the :class:`Subscriber` as a context manager:

.. code-block::

    async with Subscriber(server=server, metrics=metrics, expires=....) as subscriber:
        # ... run task

The most important parameter here is the `expires`. As the connection is closed to 
MetricQ, the created subscription may never be stopped, if the program gets 
terminated, the `expires` parameter is required. It represents the time until the
MetricQ server will automatically delete all buffered data and is given in seconds
or a :class:`Timedelta`.

.. note::

    Per design, the :class:`Subscriber` closes the connection right after the 
    subscribe request. In particluar, in the above context, the `subscriber`
    object does not have an open connection even within the `with`-statement.


Within this `with`-context, you can now perform any task, for instance start
the measured program with :meth:`asyncio.create_subprocess_exec`.


Receive the buffered metric data
--------------------------------

Once the collection of data shall stop and we want to receive the buffered data,
we use a :class:`Drain` instance. Again, the :class:`Drain` can be used as context
manager as well as it is an iterable over the data. In particular, we can use the
following code, to connect to MetricQ, stop the buffering of incoming data, and 
fetch all currently buffered data:

.. code-block::

    async with subscriber.drain() as data:
        async for metric, time, value in data:
            # ... consume the data point