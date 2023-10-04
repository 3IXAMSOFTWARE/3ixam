
set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamtranslation
  ../../bmesh
  ../../depsgraph
  ../../gpu
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/clog
  ../../../../intern/eigen
  ../../../../intern/guardedalloc
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)

set(SRC
  gizmo_draw_utils.c
  gizmo_geometry.h
  gizmo_library_intern.h
  gizmo_library_presets.c
  gizmo_library_utils.c
  geometry/geom_arrow_gizmo.c
  geometry/geom_cube_gizmo.c
  geometry/geom_dial_gizmo.c
  gizmo_types/arrow3d_gizmo.c
  gizmo_types/blank3d_gizmo.c
  gizmo_types/button2d_gizmo.c
  gizmo_types/cage2d_gizmo.c
  gizmo_types/cage3d_gizmo.c
  gizmo_types/dial3d_gizmo.c
  gizmo_types/move3d_gizmo.c
  gizmo_types/primitive3d_gizmo.c
  gizmo_types/snap3d_gizmo.c
  gizmo_types/button2dhex_gizmo.c
  gizmo_types/button2dtria_gizmo.c
)

set(LIB
)


ixam_add_lib(bf_editor_gizmo_library "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h
add_dependencies(bf_editor_gizmo_library bf_rna)
