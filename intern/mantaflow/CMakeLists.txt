# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2019 Blender Foundation. All rights reserved.


add_definitions(-DWITH_FLUID=1)

if(WITH_OPENVDB)
  add_definitions(-DOPENVDB=1)
else()
  add_definitions(-DOPENVDB=0)
endif()

if(WIN32)
  add_definitions(-D_USE_MATH_DEFINES)
endif()


set(INC
  extern
  intern/strings
  ../../source/ixam/makesdna
  ../../source/ixam/ixamlib
)

# Python is always required
add_definitions(-DWITH_PYTHON)

set(INC_SYS
  ../../extern/mantaflow/helper/util
  ../../extern/mantaflow/helper/pwrapper
  ../../extern/mantaflow/preprocessed
  ../guardedalloc
  ${PYTHON_INCLUDE_DIRS}
  ${ZLIB_INCLUDE_DIRS}
)

if(WITH_TBB)
  list(APPEND INC_SYS
    ${TBB_INCLUDE_DIRS}
  )
  list(APPEND LIB
    ${TBB_LIBRARIES}
  )
endif()

if(WITH_OPENVDB)
  add_definitions(-DWITH_OPENVDB ${OPENVDB_DEFINITIONS})
  list(APPEND INC_SYS
    ${OPENVDB_INCLUDE_DIRS}
  )
  list(APPEND LIB
    ${OPENVDB_LIBRARIES}
  )
endif()

set(SRC
  intern/manta_python_API.cpp
  intern/manta_fluid_API.cpp
  intern/MANTA_main.cpp

  extern/manta_python_API.h
  extern/manta_fluid_API.h
  intern/MANTA_main.h
  intern/strings/fluid_script.h
  intern/strings/smoke_script.h
  intern/strings/liquid_script.h
)

set(LIB
  extern_mantaflow

  ${PYTHON_LINKFLAGS}
  ${PYTHON_LIBRARIES}
  ${ZLIB_LIBRARIES}
)

ixam_add_lib(bf_intern_mantaflow "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
