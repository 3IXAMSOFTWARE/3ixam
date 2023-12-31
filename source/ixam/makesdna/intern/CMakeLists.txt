# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2006 Blender Foundation. All rights reserved.

# message(STATUS "Configuring makesdna")

set(INC
  ..
  ../../ixamlib
  ../../imbuf
  ../../../../intern/atomic
  ../../../../intern/guardedalloc
  ${CMAKE_CURRENT_BINARY_DIR}
)

set(INC_SYS

)

set(LIB
)

add_definitions(-DWITH_DNA_GHASH)

# Needed for `mallocn.c`.
if(HAVE_MALLOC_STATS_H)
  add_definitions(-DHAVE_MALLOC_STATS_H)
endif()

set(dna_header_include_file "${CMAKE_CURRENT_BINARY_DIR}/dna_includes_all.h")
set(dna_header_string_file "${CMAKE_CURRENT_BINARY_DIR}/dna_includes_as_strings.h")

set(DNA_INCLUDE_TEXT "/* Do not edit manually, changes will be overwritten. */\n")
set(DNA_FILE_LIST "/* Do not edit manually, changes will be overwritten. */\n")
foreach(header ${SRC_DNA_INC})
  get_filename_component(dna_header_file ${header} NAME)
  string(APPEND DNA_INCLUDE_TEXT "#include \"${header}\"\n")
  string(APPEND DNA_FILE_LIST "\t\"${dna_header_file}\",\n")
endforeach()

file(GENERATE OUTPUT ${dna_header_include_file} CONTENT "${DNA_INCLUDE_TEXT}")
file(GENERATE OUTPUT ${dna_header_string_file} CONTENT "${DNA_FILE_LIST}")

# -----------------------------------------------------------------------------
# Build makesdna executable
set(SRC
  dna_utils.c
  makesdna.c
  ../../ixamlib/intern/BLI_assert.c
  ../../ixamlib/intern/BLI_ghash.c
  ../../ixamlib/intern/BLI_ghash_utils.c
  ../../ixamlib/intern/BLI_memarena.c
  ../../ixamlib/intern/BLI_mempool.c
  ../../ixamlib/intern/hash_mm2a.c  # needed by 'BLI_ghash_utils.c', not used directly.
  ../../../../intern/guardedalloc/intern/leak_detector.cc
  ../../../../intern/guardedalloc/intern/mallocn.c
  ../../../../intern/guardedalloc/intern/mallocn_guarded_impl.c
  ../../../../intern/guardedalloc/intern/mallocn_lockfree_impl.c
  ${dna_header_include_file}
  ${dna_header_string_file}
)

# SRC_DNA_INC is defined in the parent dir

add_cc_flags_custom_test(makesdna)

add_executable(makesdna ${SRC} ${SRC_DNA_INC})
setup_platform_linker_flags(makesdna)
ixam_target_include_dirs(makesdna ${INC})
ixam_target_include_dirs_sys(makesdna ${INC_SYS})

if(WIN32 AND NOT UNIX)
  target_link_libraries(makesdna ${PTHREADS_LIBRARIES})
endif()

# Output dna.c
add_custom_command(
  OUTPUT
    ${CMAKE_CURRENT_BINARY_DIR}/dna.c
    ${CMAKE_CURRENT_BINARY_DIR}/dna_type_offsets.h
    ${CMAKE_CURRENT_BINARY_DIR}/dna_verify.c
  COMMAND
    "$<TARGET_FILE:makesdna>"
    ${CMAKE_CURRENT_BINARY_DIR}/dna.c
    ${CMAKE_CURRENT_BINARY_DIR}/dna_type_offsets.h
    ${CMAKE_CURRENT_BINARY_DIR}/dna_verify.c
    ${CMAKE_SOURCE_DIR}/source/ixam/makesdna/
  DEPENDS makesdna
)


# -----------------------------------------------------------------------------
# Build bf_dna library
set(SRC
  dna_defaults.c
  dna_genfile.c
  dna_utils.c
  ${CMAKE_CURRENT_BINARY_DIR}/dna.c
  ${CMAKE_CURRENT_BINARY_DIR}/dna_verify.c
  ${SRC_DNA_INC}

  ${CMAKE_CURRENT_BINARY_DIR}/dna_type_offsets.h
  dna_rename_defs.h
  dna_utils.h
)

set_source_files_properties(
  ${CMAKE_CURRENT_BINARY_DIR}/dna.c
  ${CMAKE_CURRENT_BINARY_DIR}/dna_type_offsets.h
  ${CMAKE_CURRENT_BINARY_DIR}/dna_verify.c
  PROPERTIES GENERATED TRUE
)

ixam_add_lib(bf_dna "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")


# -----------------------------------------------------------------------------
# Build bf_dna_ixamlib library
set(INC
  ..
  ../../ixamlib
  ../../../../intern/atomic
  ../../../../intern/guardedalloc
)

set(INC_SYS

)

set(SRC
  ../../ixamlib/intern/BLI_assert.c
  ../../ixamlib/intern/BLI_ghash.c
  ../../ixamlib/intern/BLI_ghash_utils.c
  ../../ixamlib/intern/BLI_linklist.c
  ../../ixamlib/intern/BLI_memarena.c
  ../../ixamlib/intern/BLI_mempool.c
  ../../ixamlib/intern/endian_switch.c
  ../../ixamlib/intern/hash_mm2a.c
  ../../ixamlib/intern/listbase.c

  ${SRC_DNA_DEFAULTS_INC}
)

set(LIB
)

ixam_add_lib(bf_dna_ixamlib "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
