

set(INC
  .
)

set(INC_SYS

)

set(SRC
  wcwidth.c

  wcwidth.h
)

set(LIB
)

ixam_add_lib(extern_wcwidth "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
