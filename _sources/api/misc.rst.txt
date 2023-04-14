Miscellaneous
=============

.. py:currentmodule:: metricq

Timestamps
----------

.. autoclass:: Timestamp
    :members:
    :special-members: __str__, __lt__, __eq__, __add__

Timedeltas (Durations)
----------------------

.. autoclass:: Timedelta
    :members:
    :special-members:
        __str__,
        __mul__,
        __truediv__,
        __floordiv__,

Time-value pairs and aggregates
-------------------------------


.. autoclass:: TimeValue
    :members:
    :undoc-members:

.. autoclass:: TimeAggregate
    :members:
    :undoc-members:
    :member-order: bysource

Helper types
------------

.. autoclass:: Metric

.. autoclass:: JsonDict


RPC handling
------------

.. autodecorator:: metricq.rpc_handler
