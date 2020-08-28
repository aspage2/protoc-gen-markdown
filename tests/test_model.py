import pytest
from google.protobuf.descriptor_pb2 import FieldDescriptorProto

from auto_proto_doc.model import DataType, FieldType


@pytest.mark.parametrize(
    "typ,exp",
    [
        (DataType.INT_32, True),
        (DataType.STRING, True),
        (DataType.MESSAGE, False),
        (DataType.ENUM, False),
    ],
)
def test_fieldtype_is_primitive(typ, exp):
    f = FieldType(id=typ, name="")
    assert f.is_primitive is exp


def test_fieldtype_is_enum():
    assert FieldType(id=DataType.ENUM, name="").is_enum


def test_fieldtype_is_message():
    assert FieldType(id=DataType.MESSAGE, name="").is_message


def test_make_field_type():
    p = FieldDescriptorProto(
        name="fieldname",
        number=3,
        type_name=".MyMessage",
        type=FieldDescriptorProto.Type.TYPE_MESSAGE,
    )

    ft = FieldType.make(p)
    assert ft.is_message
    assert ft.name == ".MyMessage"


def test_make_field_type_primitive():
    p = FieldDescriptorProto(
        name="fieldname", number=3, type=FieldDescriptorProto.Type.TYPE_INT32,
    )
    ft = FieldType.make(p)
    assert ft.is_primitive
    assert ft.name == "int32"
