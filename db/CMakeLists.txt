cmake_minimum_required(VERSION 3.22)

find_program(CMAKE_C_COMPILER clang-14)
find_program(CMAKE_CXX_COMPILER clang++-14)

project(cnfe)

set(CXX_STANDARD c++17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)
find_package(GMP REQUIRED)
find_package(MariaDB REQUIRED)

set(EIGEN_BUILD_DOC OFF)
set(BUILD_TESTING OFF)
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/3rd-party/eigen")

add_compile_options(-g -Og)
add_compile_definitions(DEBUG)
include_directories(include)

add_library(libgmp STATIC IMPORTED)
set_target_properties(libgmp PROPERTIES IMPORTED_LOCATION ${GMP_LIBRARIES})

add_library(cnfe-dec SHARED src/lin/main.cpp src/lin/lin.cpp src/quad/main.cpp
                            src/quad/quad.cpp)
target_link_libraries(cnfe-dec PRIVATE gmp gmpxx eigen mariadb)
target_include_directories(cnfe-dec PRIVATE ${GMP_INCLUDES} ${GMPXX_INCLUDES}
                                            ${MARIADB_INCLUDE_DIR})
