# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamtranslation
  ../../bmesh
  ../../depsgraph
  ../../geometry
  ../../gpu
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/eigen
  ../../../../intern/guardedalloc
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)


set(SRC
  uvedit_buttons.c
  uvedit_draw.c
  uvedit_islands.cc
  uvedit_ops.c
  uvedit_path.c
  uvedit_rip.c
  uvedit_select.c
  uvedit_smart_stitch.c
  uvedit_unwrap_ops.c

  uvedit_intern.h
)

set(LIB
  bf_bmesh
)


ixam_add_lib(bf_editor_uvedit "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h
add_dependencies(bf_editor_uvedit bf_rna)
