Common client operation
-----------------------

.. py:currentmodule:: metricq

All clients (:class:`Source`, :class:`Sink`, :class:`HistoryClient`, etc.) inherit from the common base class below.
Use its methods to :meth:`run<Client.run>` or :meth:`stop<Client.stop>` a client,
or :meth:`connect<Client.connect>` to the MetricQ network if you derive a custom client.

.. autoclass:: metricq.Client
    :members:
    :inherited-members:
    :no-private-members:

----

The following method is not part of the public API, but is included for reference:

.. automethod:: metricq.Agent.rpc
