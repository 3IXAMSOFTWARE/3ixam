# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../gpu
  ../../makesdna
  ../../makesrna
  ../../windowmanager
  ../../../../intern/guardedalloc

  # dna_type_offsets.h
  ${CMAKE_CURRENT_BINARY_DIR}/../../makesdna/intern
)


set(SRC
  script_edit.c
  script_ops.c
  space_script.c

  script_intern.h
)

set(LIB
)

if(WITH_PYTHON)
  list(APPEND INC
    ../../python
  )
  add_definitions(-DWITH_PYTHON)
endif()


ixam_add_lib(bf_editor_space_script "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# dna_type_offsets.h
add_dependencies(bf_editor_space_script bf_dna)
