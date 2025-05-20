cmake_minimum_required(VERSION 3.10)
project(ProtobufExample)

find_package(Protobuf REQUIRED)

include_directories(${Protobuf_INCLUDE_DIRS})

set(PROTO_FILE logger_proto.proto)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

set(SOURCE_FILES encoder.cpp ${PROTO_SRCS})

add_executable(encoder ${SOURCE_FILES})

target_link_libraries(encoder ${Protobuf_LIBRARIES})
