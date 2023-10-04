

set(INC
  include
)

set(INC_SYS

)

set(SRC
  binreloc.c

  include/binreloc.h
)

set(LIB
)

add_definitions(-DENABLE_BINRELOC)


ixam_add_lib(extern_binreloc "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
