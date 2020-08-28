#!/usr/bin/env python3

import sys

from google.protobuf.compiler.plugin_pb2 import (
    CodeGeneratorRequest,
    CodeGeneratorResponse,
)
from google.protobuf.json_format import MessageToJson

req = CodeGeneratorRequest()
req.ParseFromString(sys.stdin.buffer.read())

resp = CodeGeneratorResponse()
f = resp.file.add()
f.name = "request.json"
f.content = MessageToJson(req, indent=0)

sys.stdout.buffer.write(resp.SerializeToString())
