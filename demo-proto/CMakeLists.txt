cmake_minimum_required(VERSION 3.10)
project(demo)

set(CMAKE_CXX_STANDARD 11)

# Locate encoder_lib correctly if installed
set(CMAKE_PREFIX_PATH "/usr/local/cmake")
find_package(encoder_lib REQUIRED)
find_package(Protobuf REQUIRED)

# Define executable
add_executable(main_app main.cpp)

# Include encoder_lib and Protobuf headers automatically
target_include_directories(main_app PUBLIC 
    "/usr/local/include"
    ${Protobuf_INCLUDE_DIRS}
)

# Link main_app to encoder_lib and Protobuf
target_link_libraries(main_app PRIVATE 
    encoder_lib
    ${Protobuf_LIBRARIES}
    pthread
)
