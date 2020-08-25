#!/usr/bin/env python3

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest, CodeGeneratorResponse

import jinja2 as J
import sys

from model import build_files, populate_descriptions

req = CodeGeneratorRequest()
data = sys.stdin.buffer.read()
req.ParseFromString(data)

env = J.Environment(loader=J.FileSystemLoader("./templates"))
fs = build_files(req)

tmpl = env.get_template("base.html")

resp = CodeGeneratorResponse()
for i, f in enumerate(fs):
    if f.name.lower().startswith("google"):
        continue
    populate_descriptions(f, req.proto_file[i])
    f_out = resp.file.add()
    f_out.name = (f.name.rsplit(".", 1)[0].rsplit("/", 1)[-1]) + ".html"
    f_out.content = tmpl.render(file=f)


sys.stdout.buffer.write(resp.SerializeToString())
