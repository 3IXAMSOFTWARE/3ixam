# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2011 Blender Foundation.

# Copyright 2011 3IXAM Foundation.

set(INC
  ../include
  ../../ixamfont
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../depsgraph
  ../../gpu
  ../../imbuf
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/guardedalloc

  # dna_type_offsets.h
  ${CMAKE_CURRENT_BINARY_DIR}/../../makesdna/intern
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)

set(SRC
  clip_buttons.c
  clip_dopesheet_draw.c
  clip_dopesheet_ops.c
  clip_draw.c
  clip_editor.c
  clip_graph_draw.c
  clip_graph_ops.c
  clip_ops.c
  clip_toolbar.c
  clip_utils.c
  space_clip.c
  tracking_ops.c
  tracking_ops_detect.c
  tracking_ops_orient.c
  tracking_ops_plane.c
  tracking_ops_solve.c
  tracking_ops_stabilize.c
  tracking_ops_track.c
  tracking_ops_utils.c
  tracking_select.c

  clip_intern.h
  tracking_ops_intern.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)


ixam_add_lib(bf_editor_space_clip "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# Needed so we can use dna_type_offsets.h for defaults initialization.
add_dependencies(bf_editor_space_clip bf_dna)
# RNA_prototypes.h
add_dependencies(bf_editor_space_clip bf_rna)
