# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../include
  ../../ixamfont
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
)


set(SRC
  space_text.c
  text_autocomplete.c
  text_draw.c
  text_format.c
  text_format_lua.c
  text_format_osl.c
  text_format_pov.c
  text_format_pov_ini.c
  text_format_py.c
  text_header.c
  text_ops.c
  text_undo.c

  text_format.h
  text_intern.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)


if(WITH_PYTHON)
  list(APPEND INC
    ../../python
  )
  add_definitions(-DWITH_PYTHON)
endif()


ixam_add_lib(bf_editor_space_text "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# dna_type_offsets.h
add_dependencies(bf_editor_space_text bf_dna)
