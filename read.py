import json
from dataclasses import asdict

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.json_format import MessageToDict

from model import build_files, populate_descriptions

with open('raw/data', 'rb') as f:
    req = CodeGeneratorRequest()
    req.ParseFromString(f.read())


fs = build_files(req)

for i, f in enumerate(fs):
    if f.name.startswith("google"):
        continue
    populate_descriptions(f, req.proto_file[i])
    print(json.dumps(asdict(f), indent=2))
