# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2013 Blender Foundation. All rights reserved.

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
  openimageio_api.h

  openimageio_api.cpp
)

set(LIB
)

if(WITH_OPENIMAGEIO)
  list(APPEND INC_SYS
    ${OPENIMAGEIO_INCLUDE_DIRS}
    ${BOOST_INCLUDE_DIR}
  )
  list(APPEND LIB
    ${OPENIMAGEIO_LIBRARIES}
    ${PUGIXML_LIBRARIES}
  )
  if(WITH_IMAGE_OPENEXR)
    list(APPEND INC_SYS
      ${OPENEXR_INCLUDE_DIRS}
    )
    list(APPEND LIB
      ${OPENEXR_LIBRARIES}
    )
  endif()

  list(APPEND LIB
    ${BOOST_LIBRARIES}
  )

  add_definitions(-DWITH_OPENIMAGEIO)
endif()

ixam_add_lib(bf_imbuf_openimageio "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
