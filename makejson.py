#!/usr/bin/env python3
from dataclasses import asdict

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest, CodeGeneratorResponse
import sys
import json

from auto_proto_doc.generate import build_files, populate_descriptions

req = CodeGeneratorRequest()
data = sys.stdin.buffer.read()
req.ParseFromString(data)

resp = CodeGeneratorResponse()

fs = build_files(req)

for i, f in enumerate(fs):
    if f.name.startswith("google"):
        continue

    populate_descriptions(f, req.proto_file[i])

    out_f = resp.file.add()
    out_f.name = f.name.rsplit(".", 1)[0].rsplit("/", 1)[-1] + ".json"
    out_f.content = json.dumps(asdict(f), indent=2)

sys.stdout.buffer.write(resp.SerializeToString())
