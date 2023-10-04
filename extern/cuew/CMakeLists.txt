

set(INC
  .
  include
)

set(INC_SYS

)

set(SRC
  src/cuew.c

  include/cuew.h
)

set(LIB
)

ixam_add_lib(extern_cuew "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
