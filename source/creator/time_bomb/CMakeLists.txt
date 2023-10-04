# -----------------------------------------------------------------------------
# TimeBomb - library to wrap C++ code for using Boost.Beat andBoost.ASIO, to call it from C

project("time_bomb" VERSION 1.0.0 LANGUAGES C CXX)

# Enable Position Independent Code
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# C++ Version
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(TIME_BOMB_SRC
    "${CMAKE_CURRENT_SOURCE_DIR}/private/time_bomb.cpp"
)

set(TIME_BOMB_INTERFACE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_library(time_bomb STATIC ${TIME_BOMB_SRC})
set_target_properties(time_bomb PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${TIME_BOMB_INTERFACE_DIR}
)
unset(TIME_BOMB_SRC)
unset(TIME_BOMB_INTERFACE_DIR)

# Boost.ASIO
if (NOT DEFINED LIBDIR)
  message(FATAL_ERROR "${PROJECT_NAME} - LIBDIR is not defined")
endif (NOT DEFINED LIBDIR)

if (NOT DEFINED BOOST_INCLUDE_DIR)
  set(BOOST_INCLUDE_DIR "${LIBDIR}/boost/include")
endif (NOT DEFINED BOOST_INCLUDE_DIR)

if (NOT DEFINED BOOST_INCLUDE_DIR OR NOT EXISTS "${BOOST_INCLUDE_DIR}/boost/asio.hpp")
  message(FATAL_ERROR "${PROJECT_NAME} - Boost.ASIO include dir not defined")
endif (NOT DEFINED BOOST_INCLUDE_DIR OR NOT EXISTS "${BOOST_INCLUDE_DIR}/boost/asio.hpp")

target_include_directories(time_bomb PRIVATE ${BOOST_INCLUDE_DIR})

# Boost.Beast
if (NOT DEFINED BOOST_INCLUDE_DIR OR NOT EXISTS "${BOOST_INCLUDE_DIR}/boost/beast.hpp")
  message(FATAL_ERROR "${PROJECT_NAME} - Boost.Beast include dir not defined")
endif (NOT DEFINED BOOST_INCLUDE_DIR OR NOT EXISTS "${BOOST_INCLUDE_DIR}/boost/beast.hpp")

target_include_directories(time_bomb PRIVATE ${BOOST_INCLUDE_DIR})

# OpenSSL
set(OPEN_SSL_CMAKE_PATH "${LIBDIR}/openssl/OpenSSL.cmake")
if (NOT EXISTS ${OPEN_SSL_CMAKE_PATH})
  message(FATAL_ERROR "${PROJECT_NAME} - OpenSSL.cmake not found at: ${OPEN_SSL_CMAKE_PATH}")
endif (NOT EXISTS ${OPEN_SSL_CMAKE_PATH})
set(SKIP_IMPORTING_LIB_CRYPTO OFF)
include(${OPEN_SSL_CMAKE_PATH})
target_link_libraries(time_bomb libssl libcryptossl)
target_include_directories(time_bomb PRIVATE "${LIBDIR}/openssl/include")

# Link with clog
set(CLOG_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/intern/clog")
target_link_libraries(time_bomb bf_intern_clog)
if (NOT CLOG_INCLUDE_DIR OR NOT EXISTS ${CLOG_INCLUDE_DIR})
  message(FATAL_ERROR "${PROJECT_NAME} - CLog include dir is invalid: ${CLOG_INCLUDE_DIR}")
endif (NOT CLOG_INCLUDE_DIR OR NOT EXISTS ${CLOG_INCLUDE_DIR})
target_include_directories(time_bomb PRIVATE ${CLOG_INCLUDE_DIR})

# Ixam Kernel
set(IXAM_KERNEL_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../ixam/ixamkernel")
set(IXAM_LIB_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../ixam/ixamlib")
target_link_libraries(time_bomb bf_ixamkernel bf_ixamlib)
if (NOT IXAM_KERNEL_INCLUDE_DIR OR NOT EXISTS ${IXAM_KERNEL_INCLUDE_DIR})
  message(FATAL_ERROR "${PROJECT_NAME} - IxamKernel include dir is invalid: ${IXAM_KERNEL_INCLUDE_DIR}")
endif (NOT IXAM_KERNEL_INCLUDE_DIR OR NOT EXISTS ${IXAM_KERNEL_INCLUDE_DIR})
target_include_directories(time_bomb PRIVATE ${IXAM_KERNEL_INCLUDE_DIR})
target_include_directories(time_bomb PRIVATE ${IXAM_LIB_INCLUDE_DIR})



message(STATUS "${PROJECT_NAME} - time_bomb library created")

# -----------------------------------------------------------------------------
