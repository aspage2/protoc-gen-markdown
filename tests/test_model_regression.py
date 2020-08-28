from auto_proto_doc import model
from auto_proto_doc.generate import build_files
from auto_proto_doc.model import DataType, FieldType


def test_enum(load_proto_file):
    req = load_proto_file("enum.proto")
    fs = build_files(req)

    exp = model.File(
        name="enum.proto",
        enums=[
            model.ProtoEnum(
                "TestEnum",
                values=[
                    model.ProtoEnumValue("ONE", " Value1 docstring\n"),
                    model.ProtoEnumValue("TWO", " Value2 docstring\n"),
                    model.ProtoEnumValue("THREE", " Value3 docstring\n"),
                ],
                description=" Enum docstring\n With multiple lines\n foobar\n",
            )
        ],
    )

    assert fs[0] == exp


def test_message(load_proto_file):
    req = load_proto_file("message.proto")
    fs = build_files(req)

    exp = model.File(
        name="message.proto",
        messages=[
            model.Message(
                name="What",
                fields=[
                    model.MessageField(
                        type=FieldType(id=DataType.BOOL, name="bool"), name="flag",
                    )
                ],
            ),
            model.Message(
                name="MyMessage",
                description=" Message docstring\n",
                fields=[
                    model.MessageField(
                        type=FieldType(id=DataType.INT_32, name="int32"),
                        name="intval",
                        description=" Int docstring\n",
                    ),
                    model.MessageField(
                        type=FieldType(id=DataType.STRING, name="string"),
                        name="strval",
                        description=" string docstring\n",
                    ),
                    model.MessageField(
                        type=FieldType(id=DataType.MESSAGE, name=".What"),
                        name="whatval",
                        repeated=True,
                    ),
                ],
            ),
        ],
    )

    assert fs[0] == exp
