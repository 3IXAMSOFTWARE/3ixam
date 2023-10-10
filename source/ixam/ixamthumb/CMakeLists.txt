# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2006 Blender Foundation. All rights reserved.

# -----------------------------------------------------------------------------
# Shared Thumbnail Extraction Logic

include_directories(
  ../ixamlib
  ../makesdna
  ../../../intern/guardedalloc
)

include_directories(
  SYSTEM
  ${ZLIB_INCLUDE_DIRS}
)

set(SRC
  src/ixamthumb.hh
  src/ixamthumb_extract.cc
  src/ixamthumb_png.cc
)

if(WIN32)
  # -----------------------------------------------------------------------------
  # Build `IxamThumb.dll`

  set(SRC_WIN32
    src/ixamthumb_win32.cc
    src/ixamthumb_win32.def
    src/ixamthumb_win32.rc
    src/ixamthumb_win32_dll.cc
  )

  add_definitions(-DNOMINMAX)

  add_library(IxamThumb SHARED ${SRC} ${SRC_WIN32})

  target_link_libraries(IxamThumb bf_ixamlib dbghelp.lib Version.lib)
  set_target_properties(IxamThumb PROPERTIES LINK_FLAGS_DEBUG "/NODEFAULTLIB:msvcrt")

else()
  # -----------------------------------------------------------------------------
  # Build `ixam-thumbnailer` executable

  set(SRC_CMD
    src/ixam_thumbnailer.cc
  )

  add_executable(ixam-thumbnailer ${SRC} ${SRC_CMD})
  setup_platform_linker_flags(ixam-thumbnailer)
  target_link_libraries(ixam-thumbnailer bf_ixamlib)
  target_link_libraries(ixam-thumbnailer ${PTHREADS_LIBRARIES})
endif()
