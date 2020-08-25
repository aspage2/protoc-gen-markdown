#!/usr/bin/env python3

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest, CodeGeneratorResponse
from google.protobuf.json_format import MessageToDict
import sys
import json

req = CodeGeneratorRequest()
data = sys.stdin.buffer.read()
req.ParseFromString(data)

for f in req.proto_file:
    if f.name.startswith("google"):
        continue
    data = MessageToDict(f, including_default_value_fields=True)
    resp = CodeGeneratorResponse()
    f = resp.file.add()
    f.content = json.dumps(data, indent=2).encode()
    f.name = "data.json"
    sys.stdout.buffer.write(resp.SerializeToString())
