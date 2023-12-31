# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  .
  ..
  ../intern
  ../../editors/include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamtranslation
  ../../depsgraph
  ../../imbuf
  ../../makesdna
  ../../makesrna
  ../../render
  ../../windowmanager
  ../../../../intern/guardedalloc
  ../../bmesh
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)


set(SRC
  nodes/node_texture_at.c
  nodes/node_texture_bricks.c
  nodes/node_texture_checker.c
  nodes/node_texture_combine_color.c
  nodes/node_texture_common.c
  nodes/node_texture_compose.c
  nodes/node_texture_coord.c
  nodes/node_texture_curves.c
  nodes/node_texture_decompose.c
  nodes/node_texture_distance.c
  nodes/node_texture_hueSatVal.c
  nodes/node_texture_image.c
  nodes/node_texture_invert.c
  nodes/node_texture_math.c
  nodes/node_texture_mixRgb.c
  nodes/node_texture_output.c
  nodes/node_texture_proc.c
  nodes/node_texture_rotate.c
  nodes/node_texture_scale.c
  nodes/node_texture_separate_color.c
  nodes/node_texture_texture.c
  nodes/node_texture_translate.c
  nodes/node_texture_valToNor.c
  nodes/node_texture_valToRgb.c
  nodes/node_texture_viewer.c
  node_texture_tree.c
  node_texture_util.c

  node_texture_util.h
)

set(LIB
  bf_nodes
)

ixam_add_lib(bf_nodes_texture "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h
add_dependencies(bf_nodes_texture bf_rna)
