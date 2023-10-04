
set(INC
  .
)

set(INC_SYS

)

set(SRC
  intern/curve_fit_cubic.c
  intern/curve_fit_cubic_refit.c
  intern/curve_fit_corners_detect.c

  curve_fit_nd.h
  intern/curve_fit_inline.h
  intern/generic_alloc_impl.h
  intern/generic_heap.c
  intern/generic_heap.h
)

set(LIB
)

ixam_add_lib(extern_curve_fit_nd "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
