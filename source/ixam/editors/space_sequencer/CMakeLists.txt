# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../include
  ../../ixamfont
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../depsgraph
  ../../draw
  ../../gpu
  ../../imbuf
  ../../makesdna
  ../../makesrna
  ../../sequencer
  ../../windowmanager
  ../../../../intern/atomic
  ../../../../intern/guardedalloc

  # dna_type_offsets.h
  ${CMAKE_CURRENT_BINARY_DIR}/../../makesdna/intern
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)


set(SRC
  sequencer_add.c
  sequencer_buttons.c
  sequencer_channels_draw.c
  sequencer_channels_edit.c
  sequencer_drag_drop.c
  sequencer_draw.c
  sequencer_edit.c
  sequencer_modifier.c
  sequencer_ops.c
  sequencer_preview.c
  sequencer_proxy.c
  sequencer_scopes.c
  sequencer_select.c
  sequencer_thumbnails.c
  sequencer_view.c
  space_sequencer.c

  sequencer_intern.h
)

set(LIB
  bf_editor_interface
  bf_editor_util
)

if(WITH_AUDASPACE)
  add_definitions(-DWITH_AUDASPACE)

  list(APPEND INC_SYS
    ${AUDASPACE_C_INCLUDE_DIRS}
  )
  list(APPEND LIB
    ${AUDASPACE_C_LIBRARIES}
    ${AUDASPACE_PY_LIBRARIES}
  )
endif()


ixam_add_lib(bf_editor_space_sequencer "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h dna_type_offsets.h
add_dependencies(bf_editor_space_sequencer bf_rna)
