cmake_minimum_required(VERSION 3.10)
project(dlt-filesystem)

set(CMAKE_CXX_STANDARD 11)

include(FetchContent)

# Fetch MsgPack Dependency
FetchContent_Declare(
    msgpack
    GIT_REPOSITORY https://github.com/msgpack/msgpack-c.git
    GIT_TAG master
)
FetchContent_MakeAvailable(msgpack)

# Find DLT library manually
find_library(DLT_LIB dlt REQUIRED)
find_path(DLT_INCLUDE_DIR dlt/dlt.h REQUIRED)

# Define Encoder Library (Static Library)
add_library(encoder_lib STATIC
    src/Logger.cpp
    src/Encoder.tpp
    include/Encoder.hpp  
    include/Logger.hpp  
)

# Ensure headers propagate correctly
target_include_directories(encoder_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Link encoder_lib to dependencies
target_link_libraries(encoder_lib PRIVATE ${DLT_LIB} pthread msgpackc)

# Install compiled library
install(TARGETS encoder_lib EXPORT EncoderLibTargets
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)


install(FILES include/Encoder.hpp src/Encoder.tpp include/Logger.hpp DESTINATION include)


# Export package for external projects 
install(EXPORT EncoderLibTargets FILE encoder_libConfig.cmake DESTINATION cmake)
export(EXPORT EncoderLibTargets FILE ${CMAKE_BINARY_DIR}/encoder_libConfig.cmake)
