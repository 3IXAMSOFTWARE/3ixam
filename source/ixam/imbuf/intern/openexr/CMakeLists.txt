# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2006 Blender Foundation. All rights reserved.

set(INC
  .
  ..
  ../..
  ../../../ixamkernel
  ../../../ixamlib
  ../../../makesdna
  ../../../../../intern/guardedalloc
  ../../../../../intern/utfconv
)

set(INC_SYS

)

set(SRC
  openexr_api.cpp
  openexr_api.h
)

set(LIB
)

if(WITH_IMAGE_OPENEXR)
  list(APPEND INC_SYS
    ${OPENEXR_INCLUDE_DIRS}
  )
  list(APPEND LIB
    ${OPENEXR_LIBRARIES}
  )
  add_definitions(-DWITH_OPENEXR)
endif()

ixam_add_lib(bf_imbuf_openexr "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
