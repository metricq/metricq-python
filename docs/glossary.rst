.. _glossary:

Glossary
========

The key words *"MUST"*, *"MUST NOT"*, *"REQUIRED"*, *"SHALL"*, *"SHALL NOT"*, *"SHOULD"*,
*"SHOULD NOT"*, *"RECOMMENDED"*,  *"MAY"*, and *"OPTIONAL"* in this document are to be
interpreted as described in :rfc:`2119`.

.. glossary::
    :sorted:

    Client
        An application that connects to the MetricQ network.
        It is uniquely identified on the network by its :term:`Token`.
        Clients may produce and consume data (see :term:`Source`, :term:`Sink`) or perform management tasks (see :term:`Manager`).

    Sink
        A :term:`Client` that receives :term:`Data Points <Data Point>` for one or several :term:`Metrics<Metric>` provided by other clients on the network.

        Use :class:`metricq.Sink` to build your own Sinks;
        see :ref:`sink-how-to` for a quick how-to.

    Source
        A :term:`Client` that produces :term:`Data Points <Data Point>` for one or several :term:`Metrics<Metric>`.
        These are then available for consumption by other Clients on the network.

    Manager
        A :term:`Client` responsible for managing RPC requests on the network.

    Data Point
        A *time-value pair*, describing a measurement of a measurand at a specific point in time.

    Metric
        A *named* series of *time-value pairs*, called :term:`Data Points<Data Point>`.
        Metrics are at the core of the MetricQ data exchange.
        They describe how one specific *measurand* (e.g. the temperature in room E27 in ℃, CPU utilization on system ``hal-9000`` in %) evolves over time.
        Clients must ensure the following properties for metrics they produce:

        Metric names must be *unique* on the network
            For any metric :math:`m`, at any point in time, there shall be *at most one* :term:`Source` online producing data points for :math:`m`.
            A single source may of course produce values for many distinct metrics.

        Any valid Metric must be ordered *strictly chronologically*:
            Suppose :math:`(t₁, v₁)` and :math:`(t₂, v₂)` are two Data Points of the same Metric.
            If :math:`(t₁, v₁)` is sent to the network *before* :math:`(t₂, v₂)`, then it is necessary that :math:`t₁ < t₂`.

    Token
        A string uniquely identifying a :term:`Client` on the MetricQ network.

        Tokens shall be *unique* on the network:
            Any set of Clients online at the same time must have distinct Tokens.

        Tokens should be formatted in |kebab-case|_ and have a *prefix* identifying the type of source:
            Examples of good client tokens are:

            * ``source-sysinfo-hal-9000``: a :term:`Source` measuring system information of the system ``hal-9000``, for example CPU utilization, free disc space, etc.
            * ``sink-websocket-sysinfo-display``: a :term:`Sink` build with |metricq-sink-websocket|_ that streams system information to a web frontend for display

            Optimally, a client token is written as :code:`<$type>-<$implementation>-<$instance>`.
            :code:`source-sysinfo-hal-9000` identifies a client of type Source,
            using an implementation producing system-info related metrics,
            for the concrete host (instance) :literal:`hal-9000`.

        Sometimes it is desirable for multiple instances of the same Client to be online at same.
        For example, there might be multiple users using the example Sink from :ref:`sink-how-to` at the same time to debug metric data.
        In this case it is important to distinguish different instances.
        In the above example, this is done automatically.

        Multiple instances of the same Client shall be distinguished by a unique suffix:
            Append a UUID, version 4 (according to :rfc:`4122#section-4.1.3`) as a hex string to the token like so::

                client-example-4198bdddab794e9f8d774a590651cdc1

    Metadata
        Each :term:`Metric` may be declared by a :term:`Source` with additional metadata attached.
        These are arbitrary `field`-`value` pairs where `value` is an arbitrary `JSON` values.
        See :ref:`metric-metadata` for more details.

.. |metricq-sink-websocket| replace:: ``metric-sink-websocket``
.. _metricq-sink-websocket: https://github.com/metricq/metricq-sink-websocket
.. |kebab-case| replace:: ``kebab-case``
.. _kebab-case:  https://en.wiktionary.org/wiki/kebab_case
