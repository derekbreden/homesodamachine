cmake_minimum_required(VERSION 3.21)
if(NOT DEFINED PICO_SDK_PATH AND DEFINED ENV{PICO_SDK_PATH})
  set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()
if(NOT PICO_SDK_PATH)
  message(FATAL_ERROR "Set PICO_SDK_PATH to the released Raspberry Pi pico-sdk 2.2.0 checkout")
endif()
set(PICO_BOARD pico CACHE STRING "RP2040 Pico; headered variants use this same build")
set(PICO_NO_PICOTOOL 1)
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(gun_positioner C CXX ASM)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
execute_process(COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/make_geometry.py --check
  RESULT_VARIABLE GEOMETRY_STATUS)
if(NOT GEOMETRY_STATUS EQUAL 0)
  message(FATAL_ERROR "Regenerate firmware geometry from the canonical mechanical package before building")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
  ${CMAKE_CURRENT_SOURCE_DIR}/../../hardware/printed-parts/fixtures/gun-positioner/geometry-check.json
  ${CMAKE_CURRENT_SOURCE_DIR}/geometry_generated.h)
set(POSITIONER_LOADED_PROFILE 0 CACHE STRING "0=bench;1=per-axis loaded development")
set(POSITIONER_MAX_RATE 2000 CACHE STRING "Bench2000 or loaded-development1000 count/s peak")
if((POSITIONER_LOADED_PROFILE EQUAL 0 AND NOT POSITIONER_MAX_RATE EQUAL 2000) OR
   (POSITIONER_LOADED_PROFILE EQUAL 1 AND NOT POSITIONER_MAX_RATE EQUAL 1000))
  message(FATAL_ERROR "Use bench profile0/rate2000 or loaded profile1/rate1000")
endif()
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()
add_executable(gun_positioner main.cpp)
target_link_libraries(gun_positioner pico_stdlib pico_rand hardware_adc hardware_uart hardware_watchdog)
target_compile_options(gun_positioner PRIVATE -Wall -Wextra -Werror)
target_compile_definitions(gun_positioner PRIVATE
  POSITIONER_LOADED_PROFILE=${POSITIONER_LOADED_PROFILE}
  POSITIONER_MAX_RATE=${POSITIONER_MAX_RATE}
  PICO_STDIO_USB_ENABLE_RESET_VIA_BAUD_RATE=0
  PICO_STDIO_USB_ENABLE_RESET_VIA_VENDOR_INTERFACE=0
  PICO_STDIO_USB_STDOUT_TIMEOUT_US=0
  PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS=0
  CFG_TUD_CDC_TX_BUFSIZE=2048
  CFG_TUD_CDC_RX_BUFSIZE=512)
pico_enable_stdio_usb(gun_positioner 1)
pico_enable_stdio_uart(gun_positioner 0)
pico_add_extra_outputs(gun_positioner)
