Creating a new project using :literal:`metricq`
===============================================

In this section, we explain some of the conventions that we (the :literal:`metricq`
authors) use when setting up a new project using the library.
Python packaging has many (at times confusing) options;  these conventions help
us have a consistent developer experience between projects, reducing
maintenance overhead.

In the following, we assume the project is called :literal:`metricq-example`, and all
filesystem paths are relative to the project root directory (:file:`/path/to/metricq-example/`).
The Python package build from this project is called :literal:`metricq_example`,
and its source code lives in directory :file:`metricq_example`.


Dependencies, building and installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Any new projects should use a :pep:`517`-compliant build system.
Use :literal:`setuptools` for this.
The directory :file:`metricq_example` contains the Python source code of the
project, create a new file :file:`pythonproject.toml`, and declare the
necessary build dependencies:


.. code-block:: toml

    [build-system]
    requires = ["setuptools>=40.6.0", "wheel"]
    build-backend = 'setuptools.build_meta'

This enables tools like :literal:`pip` to create packages from the project.
Then, in :file:`setup.cfg`, declare the project metadata and its runtime dependencies:

.. code-block:: ini

    # setup.cfg

    [metadata]
    name = metricq-example
    author = TU Dresden
    description = A metricq example project
    long_description = file: README.rst
    long_description_content_type = text/rst
    url = https://example.com/metricq-example
    license = BSD 3-clause "New" or "Revised License"
    license_file = LICENSE
    classifiers =
        License :: OSI Approved :: BSD License
        Programming Language :: Python :: 3

    [options]
    packages =
        metricq_example
    python_requires = >=3.8
    install_requires =
        metricq ~= 3.0
        # Your dependencies here


The entry :literal:`long_description` points to a `README` file;
use either `Markdown` (:file:`README.md`) or `RST` (:file:`README.rst`) formatting.
The content type is inferred from the file extension, but it does not hurt to set it explicitly.
Choose a license appropriate to your project and enter it; :literal:`metricq`
itself is licensed under the terms of the `BSD 3-clause "New" or "Revised License"`.

Under section :literal:`[options]`, point :literal:`packages` to the project source directory (i.e. :literal:`metricq_example`).
Remember to set a minimum required Python version to prevent issues at runtime.
In :literal:`install_requires` give a list of all runtime dependencies.

.. note::
   Use tilde requirements (:literal:`foo ~= x.y`) to prevent breakage caused
   by incompatibilities introduced in future releases of dependencies.

For compatibility with older release of :literal:`pip` and to enable `editable installs` for development,
include a dummy :file:`setup.py`:

.. code-block:: python

    # setup.py:
    from setuptools import setup

    setup()


.. note::
   Keep :file:`setup.cfg` the single source of truth for package metadata.
   Only add entries to :file:`setup.py` if they otherwise cannot be determined statically.
   A notable exception to this is build-time dependency detection:
   :literal:`metricq` itself must match the `PyPI`-version of :literal:`protobuf`
   with the host-version of :literal:`protoc`.


Command line interfaces
^^^^^^^^^^^^^^^^^^^^^^^

:literal:`setuptools` allows declaration of :ref:`python:entry-points`.
An entry point of type :literal:`console_script` makes a python function the
entry point of a script that is added to the :code:`$PATH` of your Python environment:

.. code-block:: ini

    # In setup.cfg:

    [options.entry_points]
    console_scripts =
        metricq-example = metricq_example.cli:main

The above makes the function :code:`main()` in module :file:`metricq_example/cli.py`
the entry point for an executable named :literal:`metricq-example`.

For a consistent command line experience, use the `click project <https://click.palletsprojects.com>`_.
Add :code:`click ~= 7.0` (or an `up-to-date` version) to :code:`install_requires` in :file:`setup.cfg`.
Then, decorate the script entry point with the appropriate command line arguments and options.
If you are building a :literal:`metricq` :term:`client<Client>`,
include `at least` options to configure the MetricQ network URL and a :term:`client token<Token>`:

.. code-block:: python

    # In metricq_example/cli.py:
    import click

    ...

    @click.command()
    @click.option(
        "--server",
        metavar="URL",
        default="amqp://localhost/",
        show_default=True,
        help="MetricQ server URL.",
    )
    @click.option(
        "--token",
        metavar="CLIENT_TOKEN",
        default=default,
        show_default=True,
        help="A token to identify this client on the MetricQ network.",
    )
    def main(server: str, token: str):
        ...


Project versioning
^^^^^^^^^^^^^^^^^^

In order to be a good network citizen, any MetricQ client should provide a version string when asked.
The single source of truth of a project's version should be its :code:`git` tags.
Where possible, use a `semver`-compatible version scheme.
Use :code:`setuptools_scm` as **build dependency** to create a version string that will automatically
be added to the package metadata and is accessible to code at runtime:

.. code-block:: toml

    # in pythonproject.toml

    [build-system]
    requires = [
        ..., # other build dependencies here
        "setuptools_scm[toml]~=6.0",
    ]

    # ...

    [tool.setuptools_scm]
    write_to = "metricq_example/version.py"


On installation, this will create a file :file:`metricq_example/version.py` that
includes variables :code:`version` (a :code:`str`) and :code:`version_tuple`
with the parsed version information.
Exclude this file from being tracked by :code:`git`:

.. code-block:: ini

    # in .gitignore
    metricq_example/version.py

This file *must* be included in the final package, so add it to the package manifest:

.. code-block:: ini

    # in MANIFEST.in
    metricq_example/version.py

----

The :code:`metricq` library will provide client information on request,
but you will need to supply a version string.
When building a client, declare an identifier :code:`__version__` *in the same
module* as your client class to have it be picked up automatically by the
:literal:`metricq` library:

.. code-block:: python

    # in metricq_example/client.py
    import metricq

    # import this project's version string
    from .version import version as __version__


    # This could also be a Sink, HistoryClient, etc.
    class MySource(metricq.Source):
        # __version__ will be picked up automatically as this client's version
        ...

If you prefer less magic, explicitly provide the version string to the client's
base class constructor:

.. code-block:: python

    # in metricq_example/client.py
    import metricq

    from .version import version as client_version


    class MySource(metricq.Source):
        def __init__(self, ...):
            ...
            super().__init__(client_version=client_version, ...)

When creating a new command line tool, also add a :code:`--version` option:

.. code-block:: python

    # In metricq_example/cli.py:
    import click

    from .version import version

    ...

    @click.command()
    @click.version_option(version=version)
    ...
    def main(...):
        ...


Tests
^^^^^

Linting
^^^^^^^

CI workflows
^^^^^^^^^^^^
