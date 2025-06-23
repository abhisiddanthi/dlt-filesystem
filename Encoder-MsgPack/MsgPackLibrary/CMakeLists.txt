cmake_minimum_required(VERSION 3.10)
project(EncoderLibrary)

set(CMAKE_CXX_STANDARD 17)

include(FetchContent)

FetchContent_Declare(
    msgpack
    GIT_REPOSITORY https://github.com/msgpack/msgpack-c.git
    GIT_TAG master
)
FetchContent_MakeAvailable(msgpack)

add_library(MsgPackLibrary STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/encoderMsgPack.cpp
)

target_include_directories(MsgPackLibrary
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${msgpack_SOURCE_DIR}/include
)
