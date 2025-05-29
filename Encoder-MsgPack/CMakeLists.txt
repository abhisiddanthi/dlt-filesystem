cmake_minimum_required(VERSION 3.10)
project(dlt-filesystem)

set(CMAKE_CXX_STANDARD 11)

include(FetchContent)

# FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz)
# FetchContent_MakeAvailable(json)

FetchContent_Declare(
    msgpack
    GIT_REPOSITORY https://github.com/msgpack/msgpack-c.git
    GIT_TAG master
)

FetchContent_MakeAvailable(msgpack)

# Find DLT library manually
find_library(DLT_LIB dlt REQUIRED)
find_path(DLT_INCLUDE_DIR dlt/dlt.h REQUIRED)

include_directories(${DLT_INCLUDE_DIR})
include_directories(${msgpack_SOURCE_DIR}/include)

add_executable(encoder encoder.cpp)

# target_link_libraries(encoder PRIVATE nlohmann_json::nlohmann_json)
target_link_libraries(encoder PRIVATE ${DLT_LIB} pthread)