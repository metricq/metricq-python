CLI
===

This module provides CLI utilities and decorators for MetricQ applications, including custom parameter types for choices, durations, timestamps, templates, and metrics.

The main focus of this module is to standardize the CLI interfaces of different programs.

To use this part of the package you need to install additional dependencies. You can install the dependencies using the following command:

.. code-block:: bash

    pip install "metricq[cli]"

..

Decorators
----------

.. automodule:: metricq.cli.decorator
    :members: metricq_command, metricq_metric_option, metricq_server_option, metricq_token_option,


Parameter
---------
For you convenience, we provide a set of custom parameter types that you can use as custom types in your click option definitions.

.. automodule:: metricq.cli.params
    :members:
    :exclude-members: get_metavar, convert, name





