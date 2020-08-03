#!/bin/env python3
import os
import re
import subprocess
import sys
from distutils.spawn import find_executable

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

try:
    from metricq import _protobuf_version
except ImportError:
    _protobuf_version = None


def find_protoc():
    if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
        protoc = os.environ["PROTOC"]
    else:
        protoc = find_executable("protoc")

    if protoc is None:
        sys.stderr.write(
            "protoc not found. Is protobuf-compiler installed? \n"
            "Alternatively, you can point the PROTOC environment variable at a local version (current: {}).".format(
                os.environ.get("PROTOC", "Not set")
            )
        )
        sys.exit(1)

    return protoc


def get_protoc_version() -> (int, int, int):
    protoc_version_string = str(subprocess.check_output([find_protoc(), "--version"]))
    version_search = re.search(
        r"((?P<major>(0|[1-9]\d*))\.(?P<minor>(0|[1-9]\d*))\.(?P<patch>(0|[1-9]\d*)))",
        protoc_version_string,
    )

    sys.stderr.write(f"[protobuf] found protoc version {version_search.group(0)}\n")
    return tuple(int(version_search.group(g)) for g in ("major", "minor", "patch"))


def make_protobuf_requirement(major: int, minor: int, patch: int) -> str:
    """ Sometimes the versions of libprotoc and the python package `protobuf` are out of sync.

    For example, while there was protoc version 3.12.3, the latest release of
    `protobuf` was 3.12.2.  So we'll just depend on `x.y.0` and hope that
    there's no breaking changes between patches.
    """

    del patch
    return f"protobuf~={major}.{minor}.{0}"


def get_protobuf_requirement() -> str:
    if _protobuf_version:
        requirement = _protobuf_version._protobuf_requirement
        sys.stderr.write(
            f"[protobuf] read protobuf requirement from {_protobuf_version.__file__}: {requirement}\n"
        )
        return requirement

    return make_protobuf_requirement(*get_protoc_version())


def init_submodule(path: os.PathLike):
    try:
        subprocess.check_call(["git", "submodule", "update", "--init", path])
    except subprocess.CalledProcessError as e:
        sys.stderr.write(
            "warning: failed to initialize submodule at {} (process returned {})\n".format(
                path, e.returncode
            )
        )
    except Exception as e:
        sys.stderr.write(
            "warning: failed to initialize submodule at {} ({})\n".format(path, e)
        )


def make_proto(command):
    out_dir = command.get_package_dir("metricq")
    proto_dir = command.get_package_dir("metricq_proto")
    init_submodule(proto_dir)
    print("[protobuf] {}".format(proto_dir))

    proto_files = set(filter(lambda x: x.endswith(".proto"), os.listdir(proto_dir)))

    if not proto_files:
        sys.stderr.write("error: no protobuf files found in {}\n".format(proto_dir))
        sys.exit(1)

    protoc = find_protoc()

    protobuf_file_generated = False

    for proto_file in proto_files:
        source = os.path.join(proto_dir, proto_file)
        out_file = os.path.join(out_dir, proto_file.replace(".proto", "_pb2.py"))

        if not os.path.exists(out_file) or os.path.getmtime(source) > os.path.getmtime(
            out_file
        ):
            sys.stderr.write("[protobuf] {} -> {}\n".format(source, out_dir))
            subprocess.check_call(
                [
                    protoc,
                    "--proto_path=" + proto_dir,
                    "--python_out=" + out_dir,
                    os.path.join(proto_dir, proto_file),
                ]
            )
            protobuf_file_generated = True

    protobuf_version_file = os.path.join(out_dir, "_protobuf_version.py")
    if protobuf_file_generated or not os.path.exists(protobuf_version_file):
        (major, minor, patch) = get_protoc_version()

        sys.stderr.write(
            f"[protobuf] writing protobuf version to {protobuf_version_file}\n"
        )
        with open(protobuf_version_file, "w") as version_file:
            version_file.writelines(
                [
                    f'_protobuf_version = "{major}.{minor}.{patch}"\n',
                    f'_protobuf_requirement = "{make_protobuf_requirement(major, minor, patch)}"\n',
                ]
            )


class ProtoBuildPy(build_py):
    def run(self):
        make_proto(self)
        super().run()


class ProtoDevelop(develop):
    def run(self):
        self.run_command("build_py")
        super().run()


setup(
    name="metricq",
    version="1.2.0",
    author="TU Dresden",
    description="A highly-scalable, distributed metric data processing framework based on RabbitMQ",
    url="https://github.com/metricq/metricq",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
    packages=["metricq", "metricq_proto"],
    scripts=[],
    install_requires=[
        "aio-pika~=6.6",
        get_protobuf_requirement(),
        "yarl",
        "setuptools",
    ],
    extras_require={
        "examples": ["aiomonitor", "click", "click-log", "click-completion"]
    },
    cmdclass={"build_py": ProtoBuildPy, "develop": ProtoDevelop},
    package_dir={"metricq_proto": "lib/metricq-protobuf"},
    test_suite="examples",
)
