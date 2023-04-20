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

:class:`Sink` and :class:`Source` implementations further inherit from :class:`DataClient`.

.. autoclass:: metricq.DataClient
    :members:
    :private-members:

----

The Agent base class is not used directly, but referenced in the documentation of other classes.

.. autoclass:: metricq.Agent
    :members:
    :private-members:
    :undoc-members:
