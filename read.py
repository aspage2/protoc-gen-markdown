import json

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest
from google.protobuf.json_format import MessageToDict

with open('raw/data', 'rb') as f:
    req = CodeGeneratorRequest()
    req.ParseFromString(f.read())

print(json.dumps(MessageToDict(req, including_default_value_fields=True), indent=2))

