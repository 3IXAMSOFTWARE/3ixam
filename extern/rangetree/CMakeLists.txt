
set(INC
  .
)

set(SRC
  range_tree.h
  intern/generic_alloc_impl.h

  intern/range_tree.c
)

set(LIB
)

ixam_add_lib(extern_rangetree "${SRC}" "${INC}" "" "${LIB}")
