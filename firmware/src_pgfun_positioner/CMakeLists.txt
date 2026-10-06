cmake_minimum_required(VERSION 3.21)
if(NOT DEFINED PICO_SDK_PATH AND DEFINED ENV{PICO_SDK_PATH})
  set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()
if(NOT PICO_SDK_PATH)
  message(FATAL_ERROR "Set PICO_SDK_PATH to the Raspberry Pi pico-sdk 2.2.0 checkout")
endif()
set(PICO_BOARD pico CACHE STRING "SKR Pico RP2040, 2MB flash")
set(PICO_NO_PICOTOOL 1)
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(pgfun_positioner C CXX ASM)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
execute_process(COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/make_geometry.py --check
  RESULT_VARIABLE GEOMETRY_STATUS)
if(NOT GEOMETRY_STATUS EQUAL 0)
  message(FATAL_ERROR "Regenerate geometry before building")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
  ${CMAKE_CURRENT_SOURCE_DIR}/../../hardware/printed-parts/fixtures/pgfun-positioner/motion-geometry.json
  ${CMAKE_CURRENT_SOURCE_DIR}/geometry_generated.h)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()
add_executable(pgfun_positioner main.cpp)
target_link_libraries(pgfun_positioner pico_stdlib pico_rand hardware_adc hardware_uart hardware_watchdog)
target_compile_options(pgfun_positioner PRIVATE -Wall -Wextra -Werror)
target_compile_definitions(pgfun_positioner PRIVATE
  PICO_STDIO_USB_ENABLE_RESET_VIA_BAUD_RATE=0
  PICO_STDIO_USB_ENABLE_RESET_VIA_VENDOR_INTERFACE=0
  PICO_STDIO_USB_STDOUT_TIMEOUT_US=0
  PICO_STDIO_USB_CONNECT_WAIT_TIMEOUT_MS=0
  CFG_TUD_CDC_TX_BUFSIZE=2048 CFG_TUD_CDC_RX_BUFSIZE=512)
pico_enable_stdio_usb(pgfun_positioner 1)
pico_enable_stdio_uart(pgfun_positioner 0)
pico_add_extra_outputs(pgfun_positioner)
