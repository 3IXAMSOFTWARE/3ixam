

set(INC
  .
  include
)

set(INC_SYS

)

set(SRC
  src/hipew.c

  include/hipew.h
)

set(LIB
)

ixam_add_lib(extern_hipew "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
