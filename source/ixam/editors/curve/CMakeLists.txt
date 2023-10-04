
set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamtranslation
  ../../depsgraph
  ../../gpu
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/clog
  ../../../../intern/guardedalloc
  ../../../../extern/curve_fit_nd
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)

set(SRC
  curve_ops.c
  editcurve.c
  editcurve_add.c
  editcurve_paint.c
  editcurve_pen.c
  editcurve_query.c
  editcurve_select.c
  editcurve_undo.c
  editfont.c
  editfont_undo.c

  curve_intern.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
  extern_curve_fit_nd
)


ixam_add_lib(bf_editor_curve "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h
add_dependencies(bf_editor_curve bf_rna)
