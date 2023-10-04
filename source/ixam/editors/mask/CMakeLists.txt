

set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../depsgraph
  ../../gpu
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/guardedalloc
)

set(SRC
  mask_add.c
  mask_draw.c
  mask_edit.c
  mask_editaction.c
  mask_ops.c
  mask_query.c
  mask_relationships.c
  mask_select.c
  mask_shapekey.c

  mask_intern.h
)

set(LIB
)


ixam_add_lib(bf_editor_mask "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
