
set(INC
  ../include
  ../../ixamfont
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
  console_draw.c
  console_ops.c
  space_console.c

  console_intern.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)

if(WITH_PYTHON)
  add_definitions(-DWITH_PYTHON)
endif()


ixam_add_lib(bf_editor_space_console "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# dna_type_offsets.h
add_dependencies(bf_editor_space_console bf_dna)
