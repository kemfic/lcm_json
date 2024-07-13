cmake_minimum_required(VERSION 3.20)
project(lcm_msgdef LANGUAGES NONE)

# Ensure LCM is built before trying to find it
find_package(lcm REQUIRED)
include(${LCM_USE_FILE})
find_package(PythonInterp REQUIRED)

# Put all message definition files in the type directory in one list
FILE(GLOB lcm_defs "${CMAKE_CURRENT_LIST_DIR}/*.lcm")

# Generate headers from message definition
lcm_wrap_types(CPP_HEADERS cpp_headers
  PYTHON_SOURCES python_install_sources
  ${lcm_defs}) #example_message_definitions})


# Create library from all the messages
message(STATUS "${cpp_headers}")
lcm_add_library(msgdef CPP ${cpp_headers}) 
lcm_install_python( ${python_install_sources} )

target_include_directories(msgdef INTERFACE
  ${cpp_headers}
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>)


lcm_install_headers(DESTINATION include
  ${CMAKE_CURRENT_BINARY_DIR}/my_lcmtypes_export.h
  ${cpp_install_headers}
)

file(TOUCH ${CMAKE_CURRENT_BINARY_DIR}/__init__.py)

lcm_install_python(
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/py
    ${python_install_sources})

add_custom_target(msgdef_gen DEPENDS ${cpp_headers} ${python_install_sources})
