

set(INC
  .
  ..
  ../..
  ../../../ixamkernel
  ../../../ixamlib
  ../../../makesdna
  ../../../../../intern/guardedalloc
)

set(INC_SYS

)

set(SRC
  cineonlib.h
  dpxlib.h
  logImageCore.h
  logmemfile.h

  cineon_dpx.c
  cineonlib.c
  dpxlib.c
  logImageCore.c
  logmemfile.c
)

set(LIB
)

if(WITH_IMAGE_CINEON)
  add_definitions(-DWITH_CINEON)
endif()

ixam_add_lib(bf_imbuf_cineon "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
