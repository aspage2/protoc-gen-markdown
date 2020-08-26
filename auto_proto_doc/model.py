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


@dataclass
class MessageField:
    name: str
    typ: str
    is_primitive: bool  # True for primitive (non-message, non-enum) types
    repeated: bool = False
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description


@dataclass
class OneOfGroup:
    name: str
    fields: T.List[MessageField] = field(default_factory=list)
    description: str = ""

    def add_description(self, descritpion, path):
        if len(path) < 2:
            self.description = descritpion
            return


@dataclass
class Message:
    name: str
    fields: T.List[MessageField] = field(default_factory=list)
    messages: T.List['Message'] = field(default_factory=list)
    oneof_groups: T.List['OneOfGroup'] = field(default_factory=list)
    enums: T.List['ProtoEnum'] = field(default_factory=list)
    description: str = ""

    @property
    def descendants(self):
        for msg in self.messages:
            yield msg
            yield from msg.descendants

    def get_field(self, fn: int) -> MessageField:
        def _walk():
            yield from self.fields
            for o in self.oneof_groups:
                yield from o.fields

        for i, (v, _) in enumerate(zip(_walk(), range(fn+1))):
            if i == fn:
                return v

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description
            return

        fid = path[0]
        if fid == desc_proto.DescriptorProto.FIELD_FIELD_NUMBER:
            self.get_field(path[1]).add_description(description, path[2:])
        elif fid == desc_proto.DescriptorProto.NESTED_TYPE_FIELD_NUMBER:
            self.messages[path[1]].add_description(description, path[2:])
        elif fid == desc_proto.DescriptorProto.ENUM_TYPE_FIELD_NUMBER:
            self.enums[path[1]].add_description(description, path[2:])
        elif fid == desc_proto.DescriptorProto.ONEOF_DECL_FIELD_NUMBER:
            self.oneof_groups[path[1]].add_description(description, path[2:])

    @staticmethod
    def _make_message(msg, name=None):
        if name is not None:
            m = Message(".".join([name, msg.name]))
        else:
            m = Message(msg.name)

        # Create oneof groups
        for decl in msg.oneof_decl:
            m.oneof_groups.append(OneOfGroup(name=decl.name))

        # Populate fields
        for fld in msg.field:
            try:
                ts = DataType.display_string(DataType(fld.type))
                is_prim = True
            except UseMessageTypeName:
                ts = fld.type_name
                is_prim = False

            mf = MessageField(fld.name, ts, is_prim)
            if fld.label == desc_proto.FieldDescriptorProto.LABEL_REPEATED:
                mf.repeated = True
            if fld.HasField("oneof_index"):
                o = m.oneof_groups[fld.oneof_index]
                o.fields.append(mf)
            else:
                m.fields.append(mf)

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
