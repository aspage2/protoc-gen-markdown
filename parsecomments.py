#!/usr/bin/env python3

from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest, CodeGeneratorResponse

import jinja2 as J
import sys

from model import build_files, File

req = CodeGeneratorRequest()
data = sys.stdin.buffer.read()
req.ParseFromString(data)

env = J.Environment(loader=J.FileSystemLoader("./templates"))
fs = build_files(req)

tmpl = env.get_template("base.html")


def populate_descriptions(file_model: File, proto_file):
    for loc in proto_file.source_code_info.location:
        desc = []
        if loc.leading_comments:
            desc.append(loc.leading_comments)
        if loc.trailing_comments:
            desc.append(loc.trailing_comments)
        if loc.leading_detached_comments:
            desc.extend(l for l in loc.leading_detached_comments)
        if desc:
            file_model.add_description(" ".join(desc), loc.path)


resp = CodeGeneratorResponse()
for i, f in enumerate(fs):
    if f.name.lower().startswith("google"):
        continue
    populate_descriptions(f, req.proto_file[i])
    f_out = resp.file.add()
    f_out.name = (f.name.rsplit(".", 1)[0].rsplit("/", 1)[-1]) + ".html"
    f_out.content = tmpl.render(file=f)


sys.stdout.buffer.write(resp.SerializeToString())
