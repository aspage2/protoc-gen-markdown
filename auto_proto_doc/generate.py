import sys
import typing as T
from pathlib import Path

import jinja2 as J
from google.protobuf.compiler.plugin_pb2 import (
    CodeGeneratorRequest,
    CodeGeneratorResponse,
)

import auto_proto_doc
from auto_proto_doc.model import RPC, File, Message, ProtoEnum, Service


def generate():
    """generate is the entrypoint for the plugin-service logic.

    1 Receive CodeGeneratorRequest
    2 foreach file in the request:
    3     create a `model.File` structure
    4     populate object descriptions from the proto-file comments
    5     render the file to markdown
    6 Send CodeGeneratorResponse with each generated markdown file.
    """
    req = CodeGeneratorRequest()
    data = sys.stdin.buffer.read()
    req.ParseFromString(data)

    p = Path(auto_proto_doc.__file__).parent
    env = J.Environment(loader=J.FileSystemLoader(str(p / "templates")))
    fs = build_files(req)

    tmpl = env.get_template("base.md")

    resp = CodeGeneratorResponse()
    for i, f in enumerate(fs):
        # skip library protobufs
        if f.name.lower().startswith("google"):
            continue
        populate_descriptions(f, req.proto_file[i])
        f_out = resp.file.add()
        f_out.name = (f.name.rsplit(".", 1)[0].rsplit("/", 1)[-1]) + ".md"
        f_out.content = tmpl.render(file=f)

    sys.stdout.buffer.write(resp.SerializeToString())


def build_files(request: CodeGeneratorRequest) -> T.List[File]:
    files = []
    for proto_file in request.proto_file:
        f_out = File(proto_file.name)
        files.append(f_out)
        f_out.messages.extend(Message.make_message(m) for m in proto_file.message_type)
        f_out.enums.extend(ProtoEnum.make_enum(e) for e in proto_file.enum_type)
        for serv in proto_file.service:
            s = Service(serv.name, [])
            f_out.services.append(s)
            for rpc in serv.method:
                s.rpcs.append(RPC(rpc.name, rpc.input_type, rpc.output_type))

    return files


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
