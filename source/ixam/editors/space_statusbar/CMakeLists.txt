# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../gpu
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
  space_statusbar.c
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)


ixam_add_lib(bf_editor_space_statusbar "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h dna_type_offsets.h
add_dependencies(bf_editor_space_statusbar bf_rna)
