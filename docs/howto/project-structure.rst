Creating a new project for MetricQ
==================================

In this section, we explain some of the conventions that we (the :literal:`metricq`
authors) use when setting up a new project using the library.
Python packaging has many (at times confusing) options;  these conventions help
us have a consistent developer experience between projects, reducing
maintenance overhead.

In the following, we assume the project is called :literal:`metricq-example`, and all
filesystem paths are relative to the project root directory (:file:`/path/to/metricq-example/`).
The Python package built from this project is called :literal:`metricq-example`,
and its source code lives in the subdirectory :file:`metricq_example` of the project root.


Dependencies, building and installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build system
------------

Any new projects should use a :pep:`517`-compliant build system.
Use :literal:`setuptools` for this.
The directory :file:`metricq_example` contains the Python source code of the
project, create a new file :file:`pyproject.toml` in the project root,
and declare the necessary build dependencies:

.. code-block:: toml

    [build-system]
    requires = ["setuptools>=40.6.0", "wheel"]
    build-backend = 'setuptools.build_meta'

This enables tools like :literal:`pip` to create packages from the project.

Runtime dependencies
--------------------

In :file:`setup.cfg`, declare the project runtime dependencies.
Under section :literal:`[options]`, point :literal:`packages` to the project source directory (i.e. :literal:`metricq_example`).
Remember to set a minimum required Python version to prevent issues at runtime.
Under :literal:`install_requires` give a list of all runtime dependencies:

.. code-block:: ini

    # In setup.cfg:

    [options]
    packages =
        metricq_example
    python_requires = >=3.8
    install_requires =
        metricq ~= 3.0
        # Your dependencies here

.. note::
   Use *compatible release* version specifiers (:literal:`foo ~= x.y`, :pep:`440#compatible-release`)
   to prevent breakage caused by incompatibilities introduced in future releases of dependencies.

For compatibility with older release of :literal:`pip` and to enable `editable installs` for development,
include a dummy :file:`setup.py`:

.. code-block:: python

    # setup.py:
    from setuptools import setup

    setup()


.. note::
   Keep :file:`setup.cfg` the single source of truth for package metadata.
   Only add entries to :file:`setup.py` if they otherwise cannot be determined statically.
   For example, :literal:`metricq` has to determine its dependencies at build-time:
   it must install a `PyPI`-provided version of :literal:`protobuf`
   that is compatible with the host-installed version of the :literal:`protobuf`-compiler, :literal:`protoc`.


Optional dependencies
---------------------

If your project has *optional* features that requires additional dependencies,
include them in section :code:`options.extras_require` of :file:`setup.cfg`.
For each feature :code:`my_feature`, define a new *extra* that lists all
additional dependencies:

.. code-block:: ini

    # In setup.cfg:

    [options.extras_require]
    my_feature =
        foo ~= 1.0
        bar ~= 2.0
        # ... more optional dependencies here

The package can then be installed with the feature enabled like so:

.. code-block:: shell

    $ # Local installation
    $ pip install '/path/to/metricq-example[my_feature]'
    $ # Installation from PyPI
    $ pip install 'metricq-example[my_feature]'


Package metadata
----------------

Also in :file:`setup.cfg`, include relevant package metadata:

.. code-block:: ini

    # In setup.cfg:

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


The entry :literal:`long_description` points to a `README` file;
use either `Markdown` (:file:`README.md`) or `RST` (:file:`README.rst`) formatting.
The content type is inferred from the file extension, but it does not hurt to set it explicitly.
Choose a license appropriate to your project and enter it; :literal:`metricq`
itself is licensed under the terms of the `BSD 3-clause "New" or "Revised License"`.


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
Use :code:`setuptools_scm` as a **build dependency** to create a version string
that will automatically be added to the package metadata and is accessible to
code at runtime:

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


On installation, this creates a file :file:`metricq_example/version.py` that
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
but you will need to supply a *client* version string.
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


Development setup
^^^^^^^^^^^^^^^^^

To enable an easy development setup, define an extra :literal:`dev`,
that transitively includes all optional dependencies needed for a local development setup:

.. code-block:: ini

    # In setup.cfg:

    [options.extras_require]
    test =
        ... # Dependencies needed for running tests
    lint =
        ... # Dependencies needed to run linters
    dev =
        %(test)s
        %(lint)s
        ...

The string :literal:`%(foo)` includes all dependencies of extra :literal:`foo` in another extra.
Create a new *virtual environment* for this project,
and then (with this environment activated) set up a local development environment by executing

.. code-block:: shell

    $ pip install -e '.[dev]'

in the project directory.

Tests
-----

We use `pytest <pytest.org>`_ to define project tests.
Create an extra :literal:`test` that pulls :literal:`pytest`,
and :literal:`pytest-asyncio` when testing :code:`async` code:

.. code-block:: ini

    # In setup.cfg:

    [options.extras_require]
    test =
        pytest
        pytest-asyncio
    dev =
        %(test)s
        ...


Tests are usually placed `outside of application code <https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code>`_,
in files at at :file:`tests/test_*.py`.
Place tests for module :code:`metricq_example.foo` (at :file:`metricq_example/foo.py`) in :file:`tests/test_foo.py`.
For example, to test the function in module :code:`metricq_example.hello`...

.. code-block:: python

    # In metricq_example/hello.py

    def hello(name: str) -> str:
        return f"Hello, {name}!"

...create a test like so:

.. code-block:: python

    # In tests/test_hello.py

    import pytest

    from metricq_example.hello import hello

    def test_hello():
        assert hello("Tester") == "Hello, Tester!"

.. note::
   Use *absolute imports* when importing from your project,
   see the notes `here <https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code>`_.



Linting
-------

We recommend a basic set of linters that (hopefully) help producing better code:

.. code-block:: ini

    # In setup.cfg:

    [options.extras_require]
    lint =
        black
        check-manifest
        flake8 ~= 3.8
        flake8-bugbear
        isort ~= 5.0
        pre-commit
    dev =
        %(lint)s
        ...

This includes:

`black <https://black.readthedocs.io/en/stable/>`_:
    A code formatter.
    No need to spend time hand-formatting your code.

`check-manifest <https://pypi.org/project/check-manifest/>`_:
    Keeps track of all the files included in built packages.
    Prevents you from accidentally forgetting files when packaging.
    *Whooops*.

    :literal:`check-manifest` will tell you to include/exclude files in :file:`MANIFEST.in`.

`flake8 <https://flake8.pycqa.org/en/latest/>`_:
    Helps you enforce some useful code styles.
    :code:`flake8` has plugin support; :code:`flake8-bugbear` adds some helpful rules.
    A sensible default configuration includes the following:

    .. code-block:: ini

        # In setup.cfg

        [flake8]
        # Tell flake8 which packages are part of your application:
        application-import-names = metricq_example, tests
        # This is the black default:
        max-line-length = 88
        extend-exclude =
            .pytest_cache,
            # Add additional directories here to exclude from checking
            ...
        # Rules to check for
        select =
            # Regular flake8 rules
            C, E, F, W
            # flake8-bugbear rules
            B
            # pep8-naming rules
            N
        # Rules to ignore.  Add a reason why.
        ignore =
            # E203: whitespace before ':' (not PEP8 compliant)
            E203
            # E501: line too long (replaced by B950)
            E501
            # W503: line break before binary operator (not PEP8 compliant)
            W503

`isort <https://pycqa.github.io/isort/>`_:
    Automatically sorts your :code:`import` statements.
    Keeps merge conflicts in import statements to a minimum.

`pre-commit <https://pre-commit.com/>`_:
    Adds :literal:`git` hooks, that automatically run other linters.
    Configure it in :file:`.pre-commit-config.yaml`:

    .. code-block:: yaml

        default_language_version:
          python: python3.9

        repos:
        - repo: https://gitlab.com/pycqa/flake8
          rev: 3.9.2
          hooks:
          - id: flake8
        - repo: https://github.com/timothycrosley/isort
          rev: 5.8.0
          hooks:
          - id: isort
            args: ["--check", "--diff"]
        - repo: https://github.com/psf/black
          rev: 21.5b1
          hooks:
          - id: black
            args: ["--check", "--diff"]
        - repo: https://github.com/mgedmin/check-manifest
          rev: "0.46"
          hooks:
          - id: check-manifest

