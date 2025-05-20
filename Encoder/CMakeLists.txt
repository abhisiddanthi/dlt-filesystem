cmake_minimum_required(VERSION 3.10)
project(ProtobufExample)

find_package(Protobuf REQUIRED)

include_directories(${Protobuf_INCLUDE_DIRS})

set(PROTO_FILE logger.proto)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

set(SOURCE_FILES encoder.cpp ${PROTO_SRCS})

find_package(jsoncpp REQUIRED)
include_directories(${JSONCPP_INCLUDE_DIRS})

add_executable(encoder ${SOURCE_FILES})
