"""model.py defines the data model used for generating proto doc.

Each dataclass defined in this module corresponds to a node type in the protobuf
syntax tree passed to a protoc plugin through a CodeGeneratorRequest.

A model tree is built to be parallel with the input syntax tree, making it very easy
to map proto comments to node descriptions. There are three steps to rendering a doc
page for each file in the request:

 1. Build a tree parallel with the CodeGeneratorRequest syntax tree.
 2. Populate the tree's node descriptions using the location items on the request.
 3. Render the html document(s) using the fully-fleshed-out tree.
"""


import typing as T
from dataclasses import dataclass, field
from enum import Enum

import google.protobuf.descriptor_pb2 as desc_proto
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorRequest


@dataclass
class MessageField:
    name: str
    typ: str
    is_primitive: bool
    description: str = ""

    def add_description(self, description: str, path:T.List[int]):
        if len(path) < 2:
            self.description = description


@dataclass
class Message:
    name: str
    fields: T.List[MessageField]
    sub_messages: T.List['Message']
    description: str = ""

    def add_description(self, description: str, path:T.List[int]):
        if len(path) < 2:
            self.description = description
            return

        fid = path[0]
        if fid == desc_proto.DescriptorProto.FIELD_FIELD_NUMBER:
            self.fields[path[1]].add_description(description, path[2:])


@dataclass
class RPC:
    name: str
    input_type: str
    output_type: str
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description


@dataclass
class Service:
    name: str
    rpcs: T.List[RPC]
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            return
        fid = path[0]
        if fid == desc_proto.ServiceDescriptorProto.METHOD_FIELD_NUMBER:
            self.rpcs[path[1]].add_description(description, path[2:])


@dataclass
class File:
    name: str
    messages: T.List[Message] = field(default_factory=list)
    services: T.List[Service] = field(default_factory=list)
    enums: T.List['ProtoEnum'] = field(default_factory=list)

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            return
        fid = path[0]
        if fid == desc_proto.FileDescriptorProto.MESSAGE_TYPE_FIELD_NUMBER:
            self.messages[path[1]].add_description(description, path[2:])
        elif fid == desc_proto.FileDescriptorProto.SERVICE_FIELD_NUMBER:
            self.services[path[1]].add_description(description, path[2:])
        elif fid == desc_proto.FileDescriptorProto.ENUM_TYPE_FIELD_NUMBER:
            self.enums[path[1]].add_description(description, path[2:])


@dataclass
class ProtoEnum:
    name: str
    values: T.List['ProtoEnumValue']
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description
            return
        fid = path[0]
        if fid == desc_proto.EnumDescriptorProto.VALUE_FIELD_NUMBER:
            self.values[path[1]].add_description(description, path)


@dataclass
class ProtoEnumValue:
    name: str
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description


class UseMessageTypeName(Exception):
    pass


class DataType(Enum):
    STRING = 9
    INT_32 = 5
    FLOAT = 2
    MESSAGE = 11
    INT_64 = 3
    BOOL = 8
    BYTES = 12
    DOUBLE = 1
    ENUM = 14
    FIXED32 = 7
    FIXED64 = 6
    GROUP = 10

    @staticmethod
    def display_string(typ: 'DataType'):
        if typ is DataType.MESSAGE:
            raise UseMessageTypeName()
        return {
            DataType.STRING: "string",
            DataType.INT_32: "int32",
            DataType.INT_64: "int64",
            DataType.FLOAT: "float",
            DataType.BOOL: "bool",
            DataType.FIXED32: "fixed32",
            DataType.FIXED64: "fixed64",
        }[typ]


def build_files(request: CodeGeneratorRequest) -> T.List[File]:
    files = []
    for proto_file in request.proto_file:
        f_out = File(proto_file.name)
        files.append(f_out)
        for msg in proto_file.message_type:
            m = Message(msg.name, [], [])
            f_out.messages.append(m)
            for fld in msg.field:
                try:
                    ts = DataType.display_string(DataType(fld.type))
                    is_prim = True
                except UseMessageTypeName:
                    ts = fld.type_name
                    is_prim = False
                m.fields.append(MessageField(fld.name, ts, is_prim))
        for serv in proto_file.service:
            s = Service(serv.name, [])
            f_out.services.append(s)
            for rpc in serv.method:
                s.rpcs.append(RPC(rpc.name, rpc.input_type, rpc.output_type))
        for enum in proto_file.enum_type:
            e = ProtoEnum(enum.name, [])
            f_out.enums.append(e)
            for val in enum.value:
                e.values.append(ProtoEnumValue(val.name))

    return files