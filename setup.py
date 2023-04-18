#!/bin/env python3
# setuptools-imports must come before distutils-imports,
# since the former packages its own version of the latter.
#
# See https://setuptools.readthedocs.io/en/latest/deprecated/distutils-legacy.html
# isort: off
from setuptools import Command, setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

# isort: on
import importlib.util
import logging
import os
import re
import subprocess
import sys
from bisect import bisect_right
from datetime import datetime
from distutils.errors import DistutilsFileError
from distutils.log import ERROR, INFO
from distutils.spawn import find_executable
from operator import itemgetter
from typing import Any, Iterable, Optional, cast

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger()

metricq_package_dir = "metricq"
protobuf_version_module_file = "_protobuf_version.py"


class ProtocWrapper:
    @staticmethod
    def _find_protoc() -> str | None:
        if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
            return os.environ["PROTOC"]

        return find_executable("protoc")

    @staticmethod
    def _get_protoc_version(protoc: str) -> tuple[int, int, int]:
        protoc_version_string = str(subprocess.check_output([protoc, "--version"]))
        version_search = re.search(
            r"((?P<major>(0|[1-9]\d*))\.(?P<minor>(0|[1-9]\d*))\.(?P<patch>(0|[1-9]\d*)))",
            protoc_version_string,
        )

        return tuple(int(version_search.group(g)) for g in ("major", "minor", "patch"))  # type: ignore

    _executable: str | None
    _version: tuple[int, int, int] | None

    def __init__(self) -> None:
        self._executable = self._find_protoc()
        if self._executable:
            self._version = self._get_protoc_version(self._executable)
        else:
            self._version = None

    def _assert_has_executable(self) -> None:
        if self._executable is None:
            logger.error("protoc not found")
            logger.info(
                "Is protobuf-compiler installed? "
                "Alternatively, you can point the PROTOC environment variable at a local version (current: {}).\n".format(
                    os.environ.get("PROTOC", "Not set")
                )
            )
            raise DistutilsFileError("protoc not found")

    @property
    def executable(self) -> str:
        self._assert_has_executable()
        assert self._executable  # for mypy
        return self._executable

    @property
    def version(self) -> tuple[int, int, int]:
        self._assert_has_executable()
        assert self._version  # for mypy
        return self._version


protoc_wrapper = ProtocWrapper()


def make_protobuf_requirement(major: int, minor: int, patch: int) -> str:
    """
    We need to figure out a compatible version range of the python protobuf
    package based on the version of the installed `protoc`. However, there is
    no clean way to determine if those versions are compatible.
    Between protobuf packages for different languages/libprotoc major versions
    may diverge for the same release, while minor and patch versions align.
    Different releases may or may not be compatible...
    We can not predict which python protobuf versions will be compatible.
    Hence, for compatibility this uses the following approach:
    We hardcode a minor->major map, so the build works sort of like this
    1) get m(major).n(minor).p(patch) from protoc
    2) m' = 3 if n < 21 else 4 (as encoded in protobuf_version_mapping)
    2) depend on protobuf>=m'.n,<m'.n+1
    See also:
    - https://github.com/protocolbuffers/protobuf/issues/11123
    - https://protobuf.dev/news/2022-05-06/#python-updates
    """
    del patch  # We don't even care

    if major < 3:
        raise RuntimeError(
            "The installed protoc major version {major} is too old, "
            "at least version 3 is required."
        )

    # This encodes on which minor protobuf version the major python protobuf
    # version was bumped
    protobuf_version_mapping = (
        (3, 0),
        (4, 21),
    )

    # We must subtract one because bisect gives the insertion point after...
    py_major = protobuf_version_mapping[
        bisect_right(protobuf_version_mapping, minor, key=itemgetter(1)) - 1
    ][0]
    return f"protobuf>={py_major}.{minor}, <{py_major}.{minor+1}"


def get_protobuf_requirement_from_protoc() -> str:
    requirement = make_protobuf_requirement(*protoc_wrapper.version)
    logger.info(f"derived protobuf requirement from protoc: {requirement}")
    return requirement


def get_protobuf_requirement_from_module() -> Optional[str]:
    protobuf_version_file = os.path.join(
        metricq_package_dir, protobuf_version_module_file
    )
    try:
        # This is supposedly the way to import a source file directly.
        # We don't need to have it in sys.modules
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location(
            "_protobuf_version", protobuf_version_file
        )
        if spec is None or spec.loader is None:
            logger.warning(
                f"failed to read protobuf requirement from {protobuf_version_file}, spec empty"
            )
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        requirement = module._protobuf_requirement
        assert isinstance(requirement, str)
        logger.info(f"read protobuf requirement from module: {requirement}")
        return requirement
    except Exception as e:  # who knows what could go wrong
        logger.info(
            f"failed to read protobuf requirement from {protobuf_version_file}, {e}"
        )
        return None


protobuf_requirement_from_module = get_protobuf_requirement_from_module()


def get_protobuf_requirement() -> str:
    if protobuf_requirement_from_module is not None:
        return protobuf_requirement_from_module
    return get_protobuf_requirement_from_protoc()


def init_submodule(path: str) -> None:
    try:
        subprocess.check_call(["git", "submodule", "update", "--init", path])
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"failed to initialize submodule at {path} (process returned {e.returncode})"
        )
    except Exception as e:
        logger.warning(f"failed to initialize submodule at {path} ({e})")


class BuildProtobuf(Command):
    """Custom distutils command, registered as `build_protobuf`.

    Run `./setup.py build_protobuf --help` for usage instructions."""

    user_options = [
        ("force", "f", "force compilation of protobuf files"),
        (
            "package-dir=",
            "o",
            "directory of the metricq package where python files are generated",
        ),
        ("proto-dir=", "i", "directory where input .proto files are located"),
    ]
    force: Optional[bool] = None
    package_dir: Optional[str] = None
    proto_dir: Optional[str] = None

    def initialize_options(self) -> None:
        self.force = None
        self.package_dir = None
        self.proto_dir = None

    def finalize_options(self) -> None:
        if self.force is None:
            self.force = False

        if self.package_dir is None:
            self.package_dir = metricq_package_dir

        if self.proto_dir is None:
            self.proto_dir = "lib/metricq-protobuf/"

    def info(self, msg: str) -> None:
        self.announce(f"info: {type(self).__name__}: {msg}", level=INFO)

    def error(self, msg: str) -> None:
        self.announce(f"error: {type(self).__name__}: {msg}", level=ERROR)

    @property
    def _protobuf_filenames(self) -> Iterable[str]:
        """
        Just the file name, not the full path.
        """
        filenames = set(
            filter(lambda x: x.endswith(".proto"), os.listdir(self.proto_dir))
        )

        if not filenames:
            self.error(f"no protobuf files found in {self.proto_dir}")
            raise DistutilsFileError(f"No protobuf files found in {self.proto_dir}")

        self.info(f"found protobuf files: {filenames}")

        return filenames

    @property
    def _need_update_files(self) -> bool:
        if self.force:
            return True
        if protobuf_requirement_from_module is None:
            # must regenerate since the version module is missing
            return True

        assert self.proto_dir is not None
        assert self.package_dir is not None
        for proto_file in self._protobuf_filenames:
            source = os.path.join(self.proto_dir, proto_file)
            out_files = [
                os.path.join(self.package_dir, proto_file.replace(".proto", "_pb2.py")),
                os.path.join(
                    self.package_dir, proto_file.replace(".proto", "_pb2.pyi")
                ),
            ]
            if any([not os.path.exists(out_file) for out_file in out_files]):
                logger.info(
                    f"updating protobuf files because at least one output file "
                    f"does not exist {out_files}"
                )
                return True
            if any(
                [
                    os.path.getmtime(source) > os.path.getmtime(out_file)
                    for out_file in out_files
                ]
            ):
                logger.info(
                    f"updating protobuf files because at least one output file "
                    f"is older than the source file {out_files}"
                )
                return True
        return False

    def _compile_protobuf(self) -> None:
        self.info(f"compiling .proto files in {self.proto_dir} to {self.package_dir}")

        assert self.proto_dir is not None
        assert self.package_dir is not None
        for proto_file in self._protobuf_filenames:
            self.info(f"compiling {proto_file}")

            subprocess.check_call(
                [
                    protoc_wrapper.executable,
                    "--proto_path=" + self.proto_dir,
                    "--python_out=" + self.package_dir,
                    "--mypy_out=" + self.package_dir,
                    os.path.join(self.proto_dir, proto_file),
                ]
            )

    def _write_protobuf_version_file(self) -> None:
        (major, minor, patch) = protoc_wrapper.version
        assert self.package_dir is not None
        version_file = os.path.join(self.package_dir, protobuf_version_module_file)
        self.info(
            f"writing protobuf version ({major}.{minor}.{patch}) to {version_file}"
        )
        with open(version_file, "w") as f:
            f.writelines(
                [
                    f"# file generated on {datetime.now()}\n",
                    f'_protobuf_version = "{major}.{minor}.{patch}"\n',
                    f'_protobuf_requirement = "{make_protobuf_requirement(major, minor, patch)}"\n',
                ]
            )

    def run(self) -> None:
        assert self.proto_dir is not None
        init_submodule(self.proto_dir)

        if not self._need_update_files:
            self.info(
                f"no protobuf files need to be updated in {self.proto_dir} / {self.package_dir}"
            )
            return
        self._compile_protobuf()
        self._write_protobuf_version_file()


class ProtoBuildPy(build_py):
    def run(self) -> None:
        # Set "--force" for the build_protobuf command if "--force" was passed to build_py.
        # https://stackoverflow.com/a/57274908
        build_protobuf_cmd = self.distribution.get_command_obj("build_protobuf")
        assert build_protobuf_cmd is not None
        build_protobuf_cmd.set_undefined_options("build_py", ("force", "force"))

        self.run_command("build_protobuf")
        super().run()


class ProtoDevelop(develop):
    def run(self, *args: Any, **kwargs: Any) -> None:
        self.run_command("build_py")
        super().run(*args, **kwargs)


# For all other setuptools options, see setup.cfg
setup(
    install_requires=[
        "aio-pika~=9.0",
        get_protobuf_requirement(),
        "Deprecated~=1.2.13",
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
    packages=find_packages(include=["metricq", "metricq.*", "metricq_proto"]),
    package_dir={"metricq_proto": "lib/metricq-protobuf"},
)
