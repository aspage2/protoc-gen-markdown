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

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description


@dataclass
class Message:
    name: str
    fields: T.List[MessageField] = field(default_factory=list)
    messages: T.List['Message'] = field(default_factory=list)
    enums: T.List['ProtoEnum'] = field(default_factory=list)
    description: str = ""

    @property
    def descendants(self):
        for msg in self.messages:
            yield msg
            yield from msg.descendants

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description
            return

        fid = path[0]
        if fid == desc_proto.DescriptorProto.FIELD_FIELD_NUMBER:
            self.fields[path[1]].add_description(description, path[2:])
        elif fid == desc_proto.DescriptorProto.NESTED_TYPE_FIELD_NUMBER:
            self.messages[path[1]].add_description(description, path[2:])
        elif fid == desc_proto.DescriptorProto.ENUM_TYPE_FIELD_NUMBER:
            self.enums[path[1]].add_description(description, path[2:])

    @staticmethod
    def _make_message(msg, name=None):
        if name is not None:
            m = Message(".".join([name, msg.name]))
        else:
            m = Message(msg.name)
        # Populate fields
        for fld in msg.field:
            try:
                ts = DataType.display_string(DataType(fld.type))
                is_prim = True
            except UseMessageTypeName:
                ts = fld.type_name
                is_prim = False
            m.fields.append(MessageField(fld.name, ts, is_prim))

        # Populate sub-messages
        m.messages.extend(
            Message._make_message(submsg, m.name)
            for submsg in msg.nested_type
        )

        # Populate enums
        m.enums.extend(
            ProtoEnum.make_enum(e)
            for e in msg.enum_type
        )
        return m

    @staticmethod
    def make_message(msg: desc_proto.DescriptorProto) -> 'Message':
        return Message._make_message(msg)


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
    rpcs: T.List[RPC] = field(default_factory=list)
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

    @staticmethod
    def make_enum(enum: desc_proto.EnumDescriptorProto) -> 'ProtoEnum':
        e = ProtoEnum(enum.name, [])
        e.values.extend(
            ProtoEnumValue(val.name)
            for val in enum.value
        )
        return e


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
    """Data types for stuff"""
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
        f_out.messages.extend(
            Message.make_message(m) for m in proto_file.message_type
        )
        f_out.enums.extend(
            ProtoEnum.make_enum(e) for e in proto_file.enum_type
        )
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