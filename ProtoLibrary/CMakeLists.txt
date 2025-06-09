cmake_minimum_required(VERSION 3.10)
project(ProtoLibrary)

set(CMAKE_CXX_STANDARD 14)

find_package(Protobuf REQUIRED)
include_directories(${Protobuf_INCLUDE_DIRS})

include_directories(${CMAKE_SOURCE_DIR}/include) 

set(PROTO_FILE ${CMAKE_CURRENT_SOURCE_DIR}/../proto/logger.proto)
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

add_library(ProtoLibrary SHARED
    ${PROTO_SRCS} ${PROTO_HDRS}
    ${CMAKE_CURRENT_SOURCE_DIR}/src/encoderProto.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/encoderProto.tpp
    ${CMAKE_CURRENT_SOURCE_DIR}/include/encoderProto.hpp
)

target_include_directories(ProtoLibrary PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${Protobuf_INCLUDE_DIRS}
)

target_link_libraries(ProtoLibrary PUBLIC ${Protobuf_LIBRARIES} pthread) 

install(TARGETS ProtoLibrary EXPORT ProtoLibraryTargets
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES include/encoderProto.hpp include/encoderProto.tpp ${PROTO_HDRS} DESTINATION include)

install(EXPORT ProtoLibraryTargets FILE ProtoLibraryConfig.cmake DESTINATION cmake)
export(EXPORT ProtoLibraryTargets FILE ${CMAKE_BINARY_DIR}/cmake/ProtoLibraryConfig.cmake)