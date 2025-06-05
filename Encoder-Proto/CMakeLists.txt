cmake_minimum_required(VERSION 3.10)
project(dlt-filesystem)

set(CMAKE_CXX_STANDARD 11)

find_package(Protobuf REQUIRED)
include_directories(${Protobuf_INCLUDE_DIRS})

find_library(DLT_LIB dlt REQUIRED)
find_path(DLT_INCLUDE_DIR dlt/dlt.h REQUIRED)

# Include directories for Encoder Library
include_directories(${CMAKE_SOURCE_DIR}/include)  
include_directories(${DLT_INCLUDE_DIR})  

# Process Protobuf files
set(PROTO_FILE ${CMAKE_SOURCE_DIR}/sine_wave.proto)
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

# Define Encoder Library (Package)
add_library(encoder_lib SHARED
    src/Logger.cpp
    src/Encoder.tpp
    include/Encoder.hpp  
    include/Logger.hpp  
    ${PROTO_SRCS} ${PROTO_HDRS}  # Ensure generated proto files are compiled
)

# Ensure headers propagate correctly
target_include_directories(encoder_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${Protobuf_INCLUDE_DIRS}
)

# Link encoder_lib to dependencies
target_link_libraries(encoder_lib PRIVATE ${Protobuf_LIBRARIES} ${DLT_LIB} pthread)

# Install compiled library
install(TARGETS encoder_lib EXPORT EncoderLibTargets
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

# Install headers (Including Protobuf-generated headers)
install(FILES include/Encoder.hpp src/Encoder.tpp include/Logger.hpp ${PROTO_HDRS} DESTINATION include)

# Export package for external projects
install(EXPORT EncoderLibTargets FILE encoder_libConfig.cmake DESTINATION cmake)
export(EXPORT EncoderLibTargets FILE ${CMAKE_BINARY_DIR}/cmake/encoder_libConfig.cmake)
