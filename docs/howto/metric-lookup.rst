.. _metric-lookup:

.. py:currentmodule:: metricq

Metric lookup
=============

The method :meth:`Client.get_metrics` provides an interface for searching metrics available on the network.
Depending on the arguments passed, a different search strategy is applied.
If :code:`metadata=True`, the result will be a dictionary mapping matching metrics to their metadata.
Otherwise a plain list of matching metric names is returned.
See the API documentation at :meth:`~Client.get_metrics` for more details.

Search by regex
---------------

If the :code:`selector` is a *PCRE*-style regex, all metrics whose name matches are returned:

.. code-block::

    >>> result = await client.get_metrics(
    >>>     selector=r"elab\.ariel\..*", metadata=False, historic=True, limit=50
    >>> )

    >>> for metric in result:
    >>>     print(metric)

    elab.ariel.board.12V.power
    elab.ariel.fan.power
    elab.ariel.power
    elab.ariel.s0.dram.power
    elab.ariel.s0.package.power
    elab.ariel.s0.package.power.chunk_offset
    elab.ariel.s0.package.power.local_offset
    elab.ariel.s1.dram.power
    elab.ariel.s1.package.power
    elab.ariel.sata.12V.power
    elab.ariel.sata.5V.power
    elab.ariel.sum.power

Alternatively, passing a list of metric names to :code:`selector` matches exactly those metrics.
This is useful if you know want to retrieve metadata for a metric you already know exists.


Search by prefix/infix
----------------------

Call :meth:`~Client.get_metrics` with :code:`prefix=...` to search for metrics whose name starts with the given prefix:

.. code-block::

    >>> result = await client.get_metrics(prefix="ariel", metadata=False, limit=10)
    >>>
    >>> for metric in result:
    >>>     print(metric)

    elab.ariel.board.12V.power
    elab.ariel.board.12V.power.100Hz
    elab.ariel.board.12V.power.1Hz
    elab.ariel.board.5V.power.1Hz
    elab.ariel.fan.power
    elab.ariel.fan.power.100Hz
    elab.ariel.fan.power.1Hz
    elab.ariel.fan.power.chunk_offset
    elab.ariel.fan.power.local_offset
    elab.ariel.fan.voltage

The name of a :term:`Metric` is a string of :literal:`.`-separated *components*.
Searching for :code:`infix="ariel"` matches all metrics whose name contains the component :code:`ariel`.

.. note::
    Infix-matches work on components, so :code:`infix="ZZZ"` will *not* match :literal:`abc.dZZZe.fgh`.

.. warning::

    *Infix* lookup is not yet supported for non-historic metrics.
    You will always need to pass :code:`historic=True`!

.. code-block::

    >>> result = await client.get_metrics(infix="ariel", metadata=False, historic=True, limit=50)
    >>>
    >>> for metric in result:
    >>>     print(metric)

    elab.ariel.board.12V.power
    elab.ariel.fan.power
    elab.ariel.power
    elab.ariel.s0.dram.power
    elab.ariel.s0.package.power
    elab.ariel.s0.package.power.chunk_offset
    elab.ariel.s0.package.power.local_offset
    elab.ariel.s1.dram.power
    elab.ariel.s1.package.power
    elab.ariel.sata.12V.power
    elab.ariel.sata.5V.power
    elab.ariel.sum.power
