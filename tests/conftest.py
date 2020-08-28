import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.json_format import ParseDict


@pytest.fixture(scope="session")
def asset_proto_dir(pytestconfig):
    return Path(pytestconfig.rootdir) / "tests" / "assets" / "proto_files"


@pytest.fixture(scope="session")
def tempdir():
    with TemporaryDirectory() as d:
        yield d


@pytest.fixture
def load_proto_file(asset_proto_dir, tempdir):
    """Load a .proto file into a CodeGeneratorRequest"""

    def _load(filename):
        cmd = [
            "python",
            "-m",
            "grpc.tools.protoc",
            f"-I{asset_proto_dir}",
            "--plugin=protoc-gen-custom=tests/dump_json.py",
            f"--custom_out={tempdir}",
            str(asset_proto_dir / filename),
        ]
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        proc.wait(3)
        assert proc.returncode == 0, proc.stderr.read()
        with (Path(tempdir) / "request.json").open("rb") as f:
            req = CodeGeneratorRequest()
            ParseDict(json.loads(f.read()), req)

        return req

    return _load
