# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2006 Blender Foundation. All rights reserved.

set(INC
  .
  ../ixamfont
  ../ixamkernel
  ../ixamlib
  ../ixamtranslation
  ../depsgraph
  ../draw
  ../editors/include
  ../imbuf
  ../makesdna
  ../makesrna
  ../nodes
  ../render
  ../sequencer
  ../windowmanager
  ../../../intern/clog
  ../../../intern/guardedalloc
  ../bmesh

  # for writefile.c: dna_type_offsets.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesdna/intern
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)

set(INC_SYS
  ${ZSTD_INCLUDE_DIRS}
)

set(SRC
  ${CMAKE_SOURCE_DIR}/release/datafiles/userdef/userdef_default_theme.c
  intern/ixam_validate.cc
  intern/readblenentry.cc
  intern/readfile.cc
  intern/readfile_tempload.cc
  intern/undofile.cc
  intern/versioning_250.c
  intern/versioning_260.c
  intern/versioning_270.c
  intern/versioning_280.c
  intern/versioning_290.c
  intern/versioning_300.cc
  intern/versioning_400.cc
  intern/versioning_common.cc
  intern/versioning_cycles.c
  intern/versioning_defaults.cc
  intern/versioning_dna.c
  intern/versioning_legacy.c
  intern/versioning_userdef.c
  intern/writefile.cc

  BLO_ixam_defs.h
  BLO_ixam_validate.h
  BLO_read_write.h
  BLO_readfile.h
  BLO_undofile.h
  BLO_writefile.h
  intern/readfile.h
  intern/versioning_common.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)

if(WITH_BUILDINFO)
  add_definitions(-DWITH_BUILDINFO)
endif()

if(WITH_CODEC_FFMPEG)
  add_definitions(-DWITH_FFMPEG)
endif()

if(WITH_ALEMBIC)
  list(APPEND INC
    ../io/alembic
  )
  add_definitions(-DWITH_ALEMBIC)
endif()

if(WITH_TBB)
  list(APPEND INC_SYS
    ${TBB_INCLUDE_DIRS}
  )
  add_definitions(-DWITH_TBB)
endif()

if(WIN32)
  add_definitions(-DNOMINMAX)
endif()

ixam_add_lib(bf_ixamloader "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# needed so writefile.c can use dna_type_offsets.h
add_dependencies(bf_ixamloader bf_dna)
# RNA_prototypes.h
add_dependencies(bf_ixamloader bf_rna)

if(WITH_GTESTS)
  set(TEST_SRC
    tests/ixamfile_load_test.cc
    tests/ixamfile_loading_base_test.cc

    tests/ixamfile_loading_base_test.h
  )
  set(TEST_INC
    ../../../intern/ghost
  )
  set(TEST_LIB
    bf_ixamloader
  )
  include(GTestTesting)
  ixam_add_test_lib(bf_ixamloader_tests "${TEST_SRC}" "${INC};${TEST_INC}" "${INC_SYS}" "${LIB};${TEST_LIB}")
endif()
