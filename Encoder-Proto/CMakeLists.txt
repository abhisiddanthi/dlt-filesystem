cmake_minimum_required(VERSION 3.10)
project(dlt-filesystem)

set(CMAKE_CXX_STANDARD 14)

set(CMAKE_PREFIX_PATH "${CMAKE_SOURCE_DIR}/ProtoLibrary/build/cmake")
find_package(ProtoLibrary REQUIRED)
# find_package(Protobuf REQUIRED)
find_package(PkgConfig)

# include(FetchContent)
# FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz)
# FetchContent_MakeAvailable(json)
# target_link_libraries(encoder PRIVATE nlohmann_json::nlohmann_json)


# Find DLT library manually
find_library(DLT_LIB dlt REQUIRED)
find_path(DLT_INCLUDE_DIR dlt/dlt.h REQUIRED)

include_directories(${DLT_INCLUDE_DIR})

# include_directories(${CMAKE_SOURCE_DIR}/ProtoLibrary/include)
# link_directories(${CMAKE_SOURCE_DIR}/ProtoLibrary/build)

add_executable(encoder encoder.cpp)

# target_link_libraries(encoder PRIVATE ${Protobuf_LIBRARIES} )
target_link_libraries(encoder PRIVATE ProtoLibrary ${DLT_LIB})


find_package(ProtoLibrary REQUIRED)
target_link_libraries(encoder PRIVATE ProtoLibrary)