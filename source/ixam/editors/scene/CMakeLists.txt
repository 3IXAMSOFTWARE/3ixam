
set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamtranslation
  ../../depsgraph
  ../../makesdna
  ../../makesrna
  ../../sequencer
  ../../windowmanager
)

set(INC_SYS

)

set(SRC
  scene_edit.c
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)


ixam_add_lib(bf_editor_scene "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
