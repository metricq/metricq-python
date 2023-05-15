.. _history-client-how-to:

.. highlight:: python
.. py:currentmodule:: metricq

Fetching historical metric data
===============================

Databases connected to the MetricQ network provide historical metric data.
We can use a :class:`HistoryClient` to retrieve this data.
Compared to :ref:`sink-how-to` and :ref:`source-how-to`,
we won't need to define our own client, we can use :class:`HistoryClient` directly.

.. note::
    All code below uses :code:`async/await`, so wrap it accordingly:

    .. code-block::

        import asyncio

        async def run_history_client():
            // Example code here
            ...

        asyncio.run(run_history_client())

Connecting to the network
-------------------------

Provide the MetricQ URL to connect to and a :term:`Token` to identify the client:

.. code-block::

    >>> token = "history-example"
    >>> server = "amqps://user:pass@metricq.example.org/"

Then define the :class:`HistoryClient` and connect it to the network:

.. code-block::

    >>> client = metricq.HistoryClient(token, server, add_uuid=True)
    >>> await client.connect()

If all went well, we are ready to retrieve our data.

.. note::
    The ``add_uuid`` parameter is recommended for interactive usage.
    Client tokens connected to MetricQ must be unique, the parameter ensures this for transient clients.

Fetching metric metadata
------------------------

All metrics passing through the MetricQ network have :term:`Metadata` associated with them.
Using :meth:`~Client.get_metrics`, we can explore for which metrics there is historical data:

.. code-block::

    >>> metric = "elab.ariel.s0.dram.power"
    >>> await client.get_metrics(metric, historic=True)
    {
        'elab.ariel.s0.dram.power': {
            '_id': 'elab.ariel.s0.dram.power',
            '_rev': '779-20e76d0b06769485e428d866a40a19e9',
            'bandwidth': 'cycle',
            'rate': 20.0,
            'scope': 'last',
            'unit': 'W',
            'source': 'source-elab-lmg670',
            'date': '2020-10-02T02:00:04.325960+00:00',
            'historic': True
        }
    }

By passing :code:`historic=True`, we limit the results to metrics with historical data only.
More complicated queries are supported by :meth:`~Client.get_metrics`, see :ref:`metric-lookup` for examples.

Getting the last value of a metric
----------------------------------

To retrieve only the last value of a metric saved to a database base, use

.. code-block::

    >>> metric = "elab.ariel.s0.dram.power"
    >>> now = metricq.Timestamp.now()
    >>> (timestamp, value) = await client.history_last_value(metric)
    >>> age = now - timestamp
    >>> print(f"Last entry: {timestamp} ({age} ago) value: {value}")
    Last entry: [1607604944653649318] 2020-12-10 13:55:44.653649+01:00 (0.624169682s ago) value: 5.2123122215271


Aggregates -- summarizing a metric
----------------------------------

:dfn:`Aggregates` contain information for a metric over a specific span of time,
for example minimum/maximum/average value, sum, integral, number of data points (*count*) etc.
Use :meth:`HistoryClient.history_aggregate` to summarize a metric in this way.

In the example below, we retrieve information about the metric :literal:`elab.ariel.s0.dram.power`
over the last 10 minutes.

.. code-block::

    >>> metric = "elab.ariel.s0.dram.power"
    >>> now = metricq.Timestamp.now()
    >>> delta = metricq.Timedelta.from_string("10min")
    >>> start_time = now - delta
    >>>
    >>> aggregate = await client.history_aggregate(
    >>>     metric, start_time=start_time, end_time=now
    >>> )
    >>> print(f"Values in the last {delta.precise_string}: {aggregate}")
    Values in the last 10min: TimeAggregate(timestamp=Timestamp(1607605522779676000), minimum=4.275346755981445, maximum=11.466414451599121, sum=55397.53575706482, count=11998, integral=2770119258139.6226, active_time=599930363353)

Here, :code:`start_time` and :code:`end_time` delimit the range of values to aggregate.
Omit either of them or both to aggregate all historical values since/until some point in time.

Multiple aggregates
-------------------

If you want to retrieve multiple successive aggregates, use :meth:`HistoryClient.history_aggregate_timeline`.
It returns an iterator of aggregates where each aggregate spans at most a duration of :code:`interval_max`.

This is useful if you want to obtain a rough overview for a metric over a longer period of time.
In the example below we get an overview of a metric over the last 365 days, with each aggregate covering at most 30 days:

.. code-block::

    >>> metric = "elab.ariel.s0.dram.power"
    >>> delta = metricq.Timedelta.from_string("356d")
    >>> interval_max = metricq.Timedelta.from_string("30d")
    >>> now = metricq.Timestamp.now()
    >>> start_time = now - delta
    >>> # Fetch aggregates for values over the past 2 hours, each at most an hour long:
    >>> aggregates = await client.history_aggregate_timeline(
    >>>     metric, start_time=start_time, end_time=now, interval_max=interval_max,
    >>> )
    >>>
    >>> print(f"Values for the last {delta.precise_string}")
    >>> for aggregate in aggregates:
    >>>     print(aggregate)
    Values for the last 356d
    TimeAggregate(timestamp=Timestamp(1576000000000000000), minimum=4.092209875269113, maximum=49.750031412119604, sum=593994374.2714809, count=98658756, integral=5998410892025108.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1577000000000000000), minimum=4.029395457601895, maximum=44.29932484337397, sum=512623432.71681815, count=99704757, integral=5140939976375570.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1578000000000000000), minimum=4.070213303973638, maximum=50.991440138904906, sum=577390774.6533275, count=99734524, integral=5788576471647640.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1579000000000000000), minimum=4.08725953086385, maximum=37.54902472030519, sum=555991185.8951057, count=99468962, integral=5588739148089780.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1580000000000000000), minimum=4.085156064549348, maximum=50.646619296011, sum=522117803.496343, count=88969261, integral=5692853013069647.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1581000000000000000), minimum=4.074948972951139, maximum=37.49095530623182, sum=462386484.7307683, count=93735992, integral=4973650909724805.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1582000000000000000), minimum=4.016890013553053, maximum=31.600963661727302, sum=513875664.22672075, count=99802606, integral=5148844813659733.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1583000000000000000), minimum=4.09505560184217, maximum=32.50840513687335, sum=504241073.58503866, count=99840737, integral=5051357041124994.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1584000000000000000), minimum=3.8778002158455225, maximum=20.456466462178092, sum=566789400.6053987, count=99793322, integral=5680943171485073.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1585000000000000000), minimum=4.055744129198569, maximum=49.848274261152525, sum=577035544.1678637, count=99795005, integral=5781975868653922.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1586000000000000000), minimum=4.090598201216997, maximum=51.71097277085196, sum=428877311.4685728, count=99806981, integral=4297132066602203.5, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1587000000000000000), minimum=3.6805707983731595, maximum=41.30919786870951, sum=477295609.5058164, count=99804732, integral=4783373487851792.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1588000000000000000), minimum=4.052929845492045, maximum=46.47610932352675, sum=430180936.40338314, count=99790197, integral=4310744175027674.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1589000000000000000), minimum=4.045782289231323, maximum=35.317270364484564, sum=428285008.46617925, count=99790000, integral=4291822388062562.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1590000000000000000), minimum=4.037842717663995, maximum=36.109705217910005, sum=577227484.2884533, count=99702528, integral=5792219436779407.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1591000000000000000), minimum=4.109231486484054, maximum=25.28786822296384, sum=1266322950.8599746, count=99759123, integral=1.2692437313689422e+16, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1592000000000000000), minimum=4.012270469843231, maximum=46.371744397447735, sum=855274849.9538565, count=99503304, integral=8586157900774826.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1593000000000000000), minimum=4.018666244768894, maximum=48.16907605898412, sum=489314953.5427221, count=99769118, integral=4905119547247363.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1594000000000000000), minimum=4.021740922113744, maximum=17.19941570890925, sum=422114944.3441083, count=99777911, integral=4230758481433696.5, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1595000000000000000), minimum=3.903405893044394, maximum=17.189800217157934, sum=421671555.77031535, count=99751312, integral=4227204663817987.5, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1596000000000000000), minimum=4.0298144051392155, maximum=17.21305943793546, sum=421677696.36389875, count=99625754, integral=4232455502722522.5, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1597000000000000000), minimum=4.0443300790978025, maximum=42.501395874728, sum=425685373.62433964, count=99692006, integral=4270007113356799.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1598000000000000000), minimum=4.022798681983203, maximum=17.226152306810846, sum=422796585.7939971, count=99797773, integral=4236512307816254.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1599000000000000000), minimum=3.9020380477110543, maximum=37.198339989443255, sum=451322892.4169525, count=99748050, integral=4525474207319798.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1600000000000000000), minimum=4.059901887791767, maximum=50.497292058134455, sum=577018180.6042662, count=99565403, integral=5794758614134834.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1601000000000000000), minimum=-0.42605497043147944, maximum=36.09832763671875, sum=314934986.7391233, count=56394789, integral=5332946931093845.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1602000000000000000), minimum=4.154049873352051, maximum=50.97846984863281, sum=103712609.46623087, count=19998790, integral=5185936811198162.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1603000000000000000), minimum=-0.27197903394699097, maximum=50.9841194152832, sum=140197859.92287374, count=19998832, integral=7010239213612438.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1604000000000000000), minimum=-0.336227685213089, maximum=47.68548583984375, sum=113817063.0869138, count=19998746, integral=5691203189059035.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1605000000000000000), minimum=-0.29484596848487854, maximum=45.82585525512695, sum=183813638.73528534, count=19898286, integral=9249958538284772.0, active_time=1000000000000000)
    TimeAggregate(timestamp=Timestamp(1606000000000000000), minimum=4.137031078338623, maximum=52.33296203613281, sum=105834719.61448812, count=19998732, integral=5292031471206438.0, active_time=1000000000000000)

Note that some of the :class:`TimeAggregate` instances returned summarize almost 100 million data points (see :code:`count=...`)!
Still, we get a rough idea of how this metric behaved over the past year without expensive calculations.

Fetching raw values
-------------------

If you are interested in raw values instead of a aggregates, use :meth:`HistoryClient.history_raw_timeline`:

.. code-block::

    >>> metric = "elab.ariel.s0.dram.power"
    >>> start_time = metricq.Timestamp.from_iso8601("2020-01-01T00:00:00.0Z")
    >>> end_time = metricq.Timestamp.from_iso8601("2020-01-01T00:00:00.1Z")
    >>> values = await client.history_raw_timeline(
    >>>     metric, start_time=start_time, end_time=end_time
    >>> )
    >>> print("Raw values of the first 100ms of 2020:")
    >>> for raw_tv in  values:
    >>>     print(raw_tv)
    Raw values of the first 100ms of 2020:
    TimeValue(timestamp=Timestamp(1577836799998195277), value=6.260790772048024)
    TimeValue(timestamp=Timestamp(1577836800008200879), value=4.186786145522286)
    TimeValue(timestamp=Timestamp(1577836800018206481), value=5.189763454302634)
    TimeValue(timestamp=Timestamp(1577836800028212083), value=7.070445673918661)
    TimeValue(timestamp=Timestamp(1577836800038217685), value=4.681345060035232)
    TimeValue(timestamp=Timestamp(1577836800048223287), value=5.109750890322914)
    TimeValue(timestamp=Timestamp(1577836800058228890), value=4.449131406548784)
    TimeValue(timestamp=Timestamp(1577836800068234492), value=4.181990750389552)
    TimeValue(timestamp=Timestamp(1577836800078240094), value=6.013008404218427)
    TimeValue(timestamp=Timestamp(1577836800088245696), value=4.734305978764959)
    TimeValue(timestamp=Timestamp(1577836800098251298), value=5.0495328431393665)

Getting Pandas DataFrames
-------------------------

You can get historic data in the form of Pandas DataFrames using :class:`metricq.pandas.PandasHistoryClient`.
This is useful if you want to use the data in a Jupyter notebook or similar.

.. code-block::

   >>> metric = "elab.ariel.power"
   >>> now = metricq.Timestamp.now()
   >>> start_time = now - metricq.Timedelta.from_string("356d")
   >>> df_aggregate = await client.history_aggregate_timeline(metric, start_time=start_time, end_time=now, interval_max=metr
   >>> icq.Timedelta.from_string("30d"))
   >>> df_aggregate.describe()

                     timestamp    minimum     maximum           sum  ...        mean  mean_integral    mean_sum    integral_s
    count                   16  16.000000   16.000000  1.600000e+01  ...   16.000000      16.000000   16.000000  1.600000e+01
    mean   2022-10-28 23:33:20  44.189104  529.980508  3.469185e+09  ...   86.789200      86.789200   86.787557  1.735784e+08
    min    2022-05-08 08:53:20  22.669203  193.229156  2.754075e+09  ...   68.908942      68.908942   68.909144  1.378179e+08
    25%    2022-08-03 04:13:20  34.589550  432.339607  2.774195e+09  ...   69.429580      69.429580   69.429318  1.388592e+08
    50%    2022-10-28 23:33:20  47.969501  552.633820  2.826499e+09  ...   70.667074      70.667074   70.667066  1.413341e+08
    75%    2023-01-23 18:53:20  51.409111  700.263397  3.547542e+09  ...   88.953029      88.953029   88.989932  1.779061e+08
    max    2023-04-20 14:13:20  56.362167  765.781311  6.428447e+09  ...  160.731526     160.731526  160.725588  3.214631e+08
    std                    NaN   9.946549  200.044892  1.124721e+09  ...   28.126507      28.126507   28.119481  5.625301e+07

    [8 rows x 11 columns]

   >>> df_aggregate.dtypes

    timestamp         datetime64[ns]
    minimum                  float64
    maximum                  float64
    sum                      float64
    count                      int64
    integral_ns              float64
    active_time      timedelta64[ns]
    mean                     float64
    mean_integral            float64
    mean_sum                 float64
    integral_s               float64
    dtype: object

   >>> df_aggregate

                 timestamp    minimum     maximum           sum  ...        mean  mean_integral    mean_sum    integral_s
    0  2022-05-08 08:53:20  47.148315  706.997009  2.754075e+09  ...   68.908942      68.908942   68.909144  1.378179e+08
    1  2022-05-31 12:26:40  32.133179  765.781311  4.785220e+09  ...  119.906583     119.906583  119.833658  2.398132e+08
    2  2022-06-23 16:00:00  34.732819  632.136292  6.428447e+09  ...  160.731526     160.731526  160.725588  3.214631e+08
    3  2022-07-16 19:33:20  22.669203  698.018860  5.168078e+09  ...  129.202305     129.202305  129.202331  2.584046e+08
    4  2022-08-08 23:06:40  34.159744  508.385712  3.222007e+09  ...   80.899874      80.899874   80.947178  1.617997e+08
    5  2022-09-01 02:40:00  47.985229  204.357193  2.863051e+09  ...   71.576453      71.576453   71.576479  1.431529e+08
    6  2022-09-24 06:13:20  31.242771  564.773865  3.150994e+09  ...   78.777729      78.777729   78.778133  1.575555e+08
    7  2022-10-17 09:46:40  51.360985  497.920654  2.765528e+09  ...   69.215058      69.215058   69.213923  1.384301e+08
    8  2022-11-09 13:20:00  47.953773  715.927673  4.524147e+09  ...  113.112492     113.112492  113.118197  2.262250e+08
    9  2022-12-02 16:53:20  43.168755  469.569214  3.175613e+09  ...   79.390365      79.390365   79.390536  1.587807e+08
    10 2022-12-25 20:26:40  50.379284  540.493774  2.781286e+09  ...   69.541946      69.541946   69.541976  1.390839e+08
    11 2023-01-18 00:00:00  51.553490  694.038757  2.789947e+09  ...   69.757696      69.757696   69.757653  1.395154e+08
    12 2023-02-10 03:33:20  52.160843  193.229156  2.779623e+09  ...   69.526586      69.526586   69.526844  1.390532e+08
    13 2023-03-05 07:06:40  51.118492  219.914642  2.770629e+09  ...   69.271985      69.271985   69.271932  1.385440e+08
    14 2023-03-28 10:40:00  56.362167  320.650787  2.774088e+09  ...   69.352327      69.352327   69.352377  1.387047e+08
    15 2023-04-20 14:13:20  52.896618  747.493225  2.774231e+09  ...   69.455331      69.455331   69.454964  1.389107e+08

    [16 rows x 11 columns]

   >>> metric = "elab.ariel.power"
   >>> now = metricq.Timestamp.now()
   >>> start_time = now - metricq.Timedelta.from_string("60s")
   >>> df_raw = await client.history_raw_timeline(metric, start_time=start_time, end_time=now)
   >>> df_raw.describe()

                               timestamp        value
    count                           1185  1185.000000
    mean   2023-05-15 11:52:23.413917184    69.162772
    min    2023-05-15 11:51:53.813568892    65.281075
    25%    2023-05-15 11:52:08.608159232    68.436317
    50%    2023-05-15 11:52:23.418808064    68.911995
    75%    2023-05-15 11:52:38.213456640    69.567841
    max    2023-05-15 11:52:53.008083283   106.411224
    std                              NaN     1.668199

   >>> df_raw.dtypes

    timestamp    datetime64[ns]
    value               float64
    dtype: object

    In [10]: df_raw
    Out[10]:
                             timestamp      value
    0    2023-05-15 11:51:53.813568892  68.291107
    1    2023-05-15 11:51:53.861333276  68.396942
    2    2023-05-15 11:51:53.909105607  69.486191
    3    2023-05-15 11:51:53.956836834  69.350136
    4    2023-05-15 11:51:54.020551519  69.223305
    ...                            ...        ...
    1180 2023-05-15 11:52:52.817083231  68.900238
    1181 2023-05-15 11:52:52.864838029  68.732780
    1182 2023-05-15 11:52:52.912546963  70.029648
    1183 2023-05-15 11:52:52.960314713  69.964630
    1184 2023-05-15 11:52:53.008083283  68.362373

    [1185 rows x 2 columns]
