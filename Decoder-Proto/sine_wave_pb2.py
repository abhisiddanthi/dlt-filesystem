# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: my.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x08my.proto\x1a\x1egoogle/protobuf/wrappers.proto\"\xcb\x01\n\rSineWavePoint\x12/\n\tamplitude\x18\x01 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12/\n\tfrequency\x18\x02 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12+\n\x05phase\x18\x03 \x01(\x0b\x32\x1c.google.protobuf.DoubleValue\x12+\n\x05value\x18\x04 \x01(\x0b\x32\x1c.google.protobuf.DoubleValueb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'my_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SINEWAVEPOINT._serialized_start=45
  _SINEWAVEPOINT._serialized_end=248
# @@protoc_insertion_point(module_scope)
