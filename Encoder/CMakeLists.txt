cmake_minimum_required(VERSION 3.10)
project(dlt-filesystem)

include(FetchContent)

find_package(Protobuf REQUIRED)

include_directories(${Protobuf_INCLUDE_DIRS})

FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz)
FetchContent_MakeAvailable(json)

set(PROTO_FILE logger.proto)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

set(SOURCE_FILES encoder.cpp ${PROTO_SRCS})

add_executable(encoder ${SOURCE_FILES})

target_link_libraries(encoder PRIVATE ${Protobuf_LIBRARIES})
target_link_libraries(encoder PRIVATE nlohmann_json::nlohmann_json)