.. _upgrading:

Upgrading :literal:`metricq`
============================

:literal:`metricq` follows the `semver` versioning scheme,
so releases of new major versions contain breaking changes.
These are listed below, together with suggested steps to
take when upgrading.

`1.x` → `2.0`
-------------

Location of exception classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:currentmodule:: metricq.exceptions

All exception classes have moved into the module :mod:`metricq.exceptions`,
documented :ref:`here <exceptions>`.
If you are importing exceptions from other submodules directly, your code might
now fail with an :exc:`python:ImportError`.

:code:`AgentStoppedError`, :code:`ConnectFailedError`, :code:`ReceivedSignalError`, :code:`PublishFailedError`:
    Import them from :mod:`metricq.exceptions`, without the :literal:`...Error`-suffix:

    * :exc:`AgentStopped`
    * :exc:`ConnectFailed`
    * :exc:`ReceivedSignal`
    * :exc:`PublishFailed`

:code:`metricq.agent.RPCError`, :code:`metricq.history_client.InvalidHistoryResponse`:
    Moved to :mod:`metricq.exceptions`:

    * :exc:`RPCError`
    * :exc:`InvalidHistoryResponse`

Removed exceptions
^^^^^^^^^^^^^^^^^^

:code:`metricq.source.MetricSendError`, :code:`metricq.agent.RPCReplyError`, :code:`metricq.client.ManagementRpcPublishError`:
    Handle :exc:`PublishFailed` instead.

:code:`metricq.sink.SinkError`, :code:`metricq.sink.SinkResubscribeError`:
    Removed, the exception that caused them is raised directly.


.. py:currentmodule:: metricq

Validation of :class:`Source` chunk sizes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Previously, anything could be assigned to :attr:`Source.chunk_size`,
now only :literal:`None` (to disable automatic chunking)
and *positive* integers are accepted.
