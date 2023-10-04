
set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/clog
  ../../../../intern/guardedalloc
  ../../bmesh
)

set(SRC
  ed_undo.c
  memfile_undo.c
  undo_system_types.c

  undo_intern.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
  bf_editor_curve
  bf_editor_lattice
  bf_editor_mesh
  bf_editor_metaball
  bf_editor_physics
)

ixam_add_lib(bf_editor_undo "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
