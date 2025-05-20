cmake_minimum_required(VERSION 3.10)
project(ProtobufExample)

find_package(Protobuf REQUIRED)

include_directories(${Protobuf_INCLUDE_DIRS})

set(PROTO_FILE addressbook.proto)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

set(SOURCE_FILES main.cpp ${PROTO_SRCS})

add_executable(my_program ${SOURCE_FILES})

target_link_libraries(my_program ${Protobuf_LIBRARIES})
