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
class FieldType:
    id: "DataType"
    name: str

    @property
    def is_primitive(self):
        return not (self.is_message or self.is_enum)

    @property
    def is_message(self):
        return self.id is DataType.MESSAGE

    @property
    def is_enum(self):
        return self.id is DataType.ENUM

    @staticmethod
    def make(fld) -> "FieldType":
        _id = DataType(fld.type)
        f = FieldType(id=_id, name=fld.type_name)
        if f.is_primitive:
            f.name = f.id.name
        return f


@dataclass
class MessageField:
    name: str
    type: FieldType
    repeated: bool = False
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description

    @staticmethod
    def make(fld) -> "MessageField":
        ft = FieldType.make(fld)
        mf = MessageField(name=fld.name, type=ft)
        if fld.label == desc_proto.FieldDescriptorProto.LABEL_REPEATED:
            mf.repeated = True
        return mf


@dataclass
class OneOfGroup:
    name: str
    description: str = ""

    def add_description(self, descritpion, path):
        if len(path) < 2:
            self.description = descritpion
            return


@dataclass
class Message:
    name: str
    fields: T.List[MessageField] = field(default_factory=list)
    messages: T.List["Message"] = field(default_factory=list)
    oneof_groups: T.List["OneOfGroup"] = field(default_factory=list)
    enums: T.List["ProtoEnum"] = field(default_factory=list)
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
        elif fid == desc_proto.DescriptorProto.ONEOF_DECL_FIELD_NUMBER:
            self.oneof_groups[path[1]].add_description(description, path[2:])

    @staticmethod
    def _make(msg, name=None):
        if name is not None:
            m = Message(".".join([name, msg.name]))
        else:
            m = Message(msg.name)

        # Create oneof groups
        for decl in msg.oneof_decl:
            m.oneof_groups.append(OneOfGroup(name=decl.name))

        # Populate fields
        for fld in msg.field:
            mf = MessageField.make(fld)
            if fld.HasField("oneof_index"):
                mf.oneof = m.oneof_groups[fld.oneof_index]
            m.fields.append(mf)

        # Populate sub-messages
        m.messages.extend(Message._make(submsg, m.name) for submsg in msg.nested_type)

        # Populate enums
        for e in msg.enum_type:
            en = ProtoEnum.make_enum(e)
            en.name = ".".join([m.name, en.name])
            m.enums.append(en)
        return m

    @staticmethod
    def make(msg: desc_proto.DescriptorProto) -> "Message":
        return Message._make(msg)


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
    enums: T.List["ProtoEnum"] = field(default_factory=list)

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
    values: T.List["ProtoEnumValue"]
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description
            return
        fid = path[0]
        if fid == desc_proto.EnumDescriptorProto.VALUE_FIELD_NUMBER:
            self.values[path[1]].add_description(description, path[2:])

    @staticmethod
    def make_enum(enum: desc_proto.EnumDescriptorProto) -> "ProtoEnum":
        e = ProtoEnum(enum.name, [])
        e.values.extend(ProtoEnumValue(val.name) for val in enum.value)
        return e


@dataclass
class ProtoEnumValue:
    name: str
    description: str = ""

    def add_description(self, description: str, path: T.List[int]):
        if len(path) < 2:
            self.description = description


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

    @property
    def name(self):
        return {
            DataType.STRING: "string",
            DataType.INT_32: "int32",
            DataType.INT_64: "int64",
            DataType.FLOAT: "float",
            DataType.BOOL: "bool",
            DataType.FIXED32: "fixed32",
            DataType.FIXED64: "fixed64",
        }[self]
