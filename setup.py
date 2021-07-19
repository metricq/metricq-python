#!/bin/env python3

# setuptools-imports must come before distutils-imports,
# since the former packages its own version of the latter.
#
# See https://setuptools.readthedocs.io/en/latest/deprecated/distutils-legacy.html
from setuptools import Command, setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

import logging
import os
import re
import subprocess
import sys
from distutils.errors import DistutilsFileError
from distutils.log import ERROR, INFO
from distutils.spawn import find_executable
from typing import Optional, Tuple

import mypy_protobuf

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

try:
    from metricq import _protobuf_version
except ImportError:
    _protobuf_version = None


def find_protoc() -> str:
    if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
        protoc = os.environ["PROTOC"]
    else:
        protoc = find_executable("protoc")

    if protoc is None:
        logger.error("protoc not found")
        logger.info(
            "Is protobuf-compiler installed? "
            "Alternatively, you can point the PROTOC environment variable at a local version (current: {}).\n".format(
                os.environ.get("PROTOC", "Not set")
            )
        )
        raise DistutilsFileError("protoc not found")

    return protoc


def protoc_version(protoc: str) -> Tuple[int, int, int]:
    protoc_version_string = str(subprocess.check_output([protoc, "--version"]))
    version_search = re.search(
        r"((?P<major>(0|[1-9]\d*))\.(?P<minor>(0|[1-9]\d*))\.(?P<patch>(0|[1-9]\d*)))",
        protoc_version_string,
    )

    return tuple(int(version_search.group(g)) for g in ("major", "minor", "patch"))


def make_protobuf_requirement(major: int, minor: int, patch: int) -> str:
    """Sometimes the versions of libprotoc and the python package `protobuf` are out of sync.

    For example, while there was protoc version 3.12.3, the latest release of
    `protobuf` was 3.12.2.  So we'll just depend on `x.y.0` and hope that
    there's no breaking changes between patches.
    """

    del patch
    return f"protobuf~={major}.{minor}.{0}"


def get_protobuf_requirement() -> str:
    if _protobuf_version:
        requirement = _protobuf_version._protobuf_requirement
        logger.info(
            f"read protobuf requirement from {_protobuf_version.__file__}: {requirement}"
        )
        return requirement

    protoc = find_protoc()
    return make_protobuf_requirement(*protoc_version(protoc))


def init_submodule(path: str):
    try:
        subprocess.check_call(["git", "submodule", "update", "--init", path])
    except subprocess.CalledProcessError as e:
        logger.warn(
            f"failed to initialize submodule at {path} (process returned {e.returncode})"
        )
    except Exception as e:
        logger.warn(f"failed to initialize submodule at {path} ({e})")


class BuildProtobuf(Command):
    """Custom distutils command, registered as `build_protobuf`.

    Run `./setup.py build_protobuf --help` for usage instructions."""

    user_options = [
        ("force", "f", "force compilation of protobuf files"),
        ("out-dir=", "o", "directory to put genenerated python files in"),
        ("proto-dir=", "i", "directory where input .proto files are located"),
    ]

    def initialize_options(self):
        self._protoc: Optional[str] = None
        self._protoc_version: Optional[Tuple[int, int, int]] = None

        self.force: Optional[bool] = None
        self.out_dir: Optional[str] = None
        self.proto_dir: Optional[str] = None

    def finalize_options(self):
        if self.force is None:
            self.force = False

        if self.out_dir is None:
            self.out_dir = "metricq/"

        if self.proto_dir is None:
            self.proto_dir = "lib/metricq-protobuf/"

    @property
    def protoc(self) -> str:
        if self._protoc is None:
            self._protoc = find_protoc()

        return self._protoc

    @property
    def protoc_version(self) -> Tuple[int, int, int]:
        if self._protoc_version is None:
            self._protoc_version = protoc_version(self.protoc)

        return self._protoc_version

    def info(self, msg):
        self.announce(f"info: {type(self).__name__}: {msg}", level=INFO)

    def error(self, msg):
        self.announce(f"error: {type(self).__name__}: {msg}", level=ERROR)

    def run(self):
        init_submodule(self.proto_dir)
        self.info(f"compiling .proto files in {self.proto_dir}")

        proto_files = set(
            filter(lambda x: x.endswith(".proto"), os.listdir(self.proto_dir))
        )

        if not proto_files:
            self.error(f"no protobuf files found in {self.proto_dir}")
            raise DistutilsFileError(f"No protobuf files found in {self.proto_dir}")

        protobuf_file_generated = False

        for proto_file in proto_files:
            source = os.path.join(self.proto_dir, proto_file)
            out_files = [
                os.path.join(self.out_dir, proto_file.replace(".proto", "_pb2.py")),
                os.path.join(self.out_dir, proto_file.replace(".proto", "_pb2.pyi")),
            ]

            if (
                self.force
                or any([not os.path.exists(out_file) for out_file in out_files])
                or any(
                    [
                        os.path.getmtime(source) > os.path.getmtime(out_file)
                        for out_file in out_files
                    ]
                )
            ):
                self.info("compiling {} -> {}".format(source, out_files))

                protoc_call_args = [
                    self.protoc,
                    "--proto_path=" + self.proto_dir,
                    "--python_out=" + self.out_dir,
                ]
                if mypy_protobuf:
                    protoc_call_args.append("--mypy_out=" + self.out_dir)

                protoc_call_args.append(os.path.join(self.proto_dir, proto_file))
                subprocess.check_call(protoc_call_args)
                protobuf_file_generated = True

        protobuf_version_file = os.path.join(self.out_dir, "_protobuf_version.py")
        if (
            self.force
            or protobuf_file_generated
            or not os.path.exists(protobuf_version_file)
        ):
            self._write_protobuf_version_file(protobuf_version_file)

    def _write_protobuf_version_file(self, version_file):
        (major, minor, patch) = self.protoc_version

        self.info(
            f"writing protobuf version ({major}.{minor}.{patch}) to {version_file}"
        )
        with open(version_file, "w") as f:
            f.writelines(
                [
                    f'_protobuf_version = "{major}.{minor}.{patch}"\n',
                    f'_protobuf_requirement = "{make_protobuf_requirement(major, minor, patch)}"\n',
                ]
            )


class ProtoBuildPy(build_py):
    def run(self):
        # God almigthy is python packaging a clusterfuck.  Set "--force" for
        # the build_protobuf command if "--force" was passed to build_py.
        #
        # https://stackoverflow.com/a/57274908
        build_protobuf_cmd: BuildProtobuf = self.distribution.get_command_obj(
            "build_protobuf"
        )
        build_protobuf_cmd.set_undefined_options("build_py", ("force", "force"))

        self.run_command("build_protobuf")
        super().run()


class ProtoDevelop(develop):
    def run(self):
        self.run_command("build_py")
        super().run()


# For all other setuptools options, see setup.cfg
setup(
    install_requires=[
        # TODO remove outer client_properties in metricq.agent.Agent.make_connection with aiormq >= 5.1.1, which might
        #  be available with the next aio-pika release
        "aio-pika~=6.7, >=6.7.1",
        get_protobuf_requirement(),
        "python-dateutil ~= 2.8, >=2.8.1",
        "yarl",
        "setuptools",
    ],
    cmdclass={
        "build_protobuf": BuildProtobuf,
        "build_py": ProtoBuildPy,
        "develop": ProtoDevelop,
    },
    include_package_data=True,
)
