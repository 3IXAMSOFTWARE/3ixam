# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2016 Blender Foundation. All rights reserved.


set(INC
  src
  src/gflags
)

set(INC_SYS
)

set(SRC
  src/gflags.cc
  src/gflags_completions.cc
  src/gflags_reporting.cc

  src/gflags/config.h
  src/gflags/gflags_completions.h
  src/gflags/gflags_declare.h
  src/gflags/gflags_gflags.h
  src/gflags/gflags.h
  src/mutex.h
  src/util.h
)

set(LIB
)

if(WIN32)
  list(APPEND SRC
    src/windows_port.cc
    src/windows_port.h
  )
endif()

add_definitions(${GFLAGS_DEFINES})

ixam_add_lib(extern_gflags "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
