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


def get_protoc_version():
    protoc_version_string = str(subprocess.check_output([find_protoc(), "--version"]))
    protoc_version = re.search(
        r"(?P<version>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))", protoc_version_string
    ).group("version")

    return protoc_version


def get_protobuf_requirement():
    if _protobuf_version:
        return _protobuf_version.__protobuf_requirement__

    return "protobuf=={}".format(get_protoc_version())


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

    if protobuf_file_generated:
        protoc_version = get_protoc_version()

        with open(os.path.join(out_dir, "_protobuf_version.py"), "w") as version_file:
            version_file.writelines(
                [
                    "__protobuf_version__ = '{}'\n".format(protoc_version),
                    "__protobuf_requirement__ = 'protobuf=={}'".format(protoc_version),
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
    version="1.1.3",
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
        "aio-pika~=6.0,>=6.4.0",
        "aiormq~=3.0",  # TODO: remove once aio-pika reexports ChannelInvalidStateError
        get_protobuf_requirement(),
        "yarl",
    ],
    extras_require={
        "examples": ["aiomonitor", "click", "click-log", "click-completion"]
    },
    cmdclass={"build_py": ProtoBuildPy, "develop": ProtoDevelop},
    package_dir={"metricq_proto": "lib/metricq-protobuf"},
    test_suite="examples",
)
