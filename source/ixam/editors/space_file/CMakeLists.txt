# SPDX-License-Identifier: GPL-2.0-or-later

set(INC
  ../asset
  ../include
  ../../ixamfont
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../gpu
  ../../imbuf
  ../../makesdna
  ../../makesrna
  ../../render
  ../../windowmanager
  ../../../../intern/atomic
  ../../../../intern/guardedalloc

  # dna_type_offsets.h
  ${CMAKE_CURRENT_BINARY_DIR}/../../makesdna/intern
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)

set(SRC
  asset_catalog_tree_view.cc
  file_draw.c
  file_indexer.cc
  file_ops.c
  file_panels.c
  file_utils.c
  filelist.cc
  filesel.c
  folder_history.cc
  fsmenu.c
  space_file.c

  file_indexer.h
  file_intern.h
  filelist.h
  fsmenu.h
)

set(LIB
  bf_ixamkernel
)

if(WITH_HEADLESS)
  add_definitions(-DWITH_HEADLESS)
else()
  list(APPEND LIB
    bf_editor_datafiles
  )
endif()

if(WITH_IMAGE_OPENEXR)
  add_definitions(-DWITH_OPENEXR)
endif()

if(WITH_OPENIMAGEIO)
  add_definitions(-DWITH_OPENIMAGEIO)
endif()

if(WITH_IMAGE_TIFF)
  add_definitions(-DWITH_TIFF)
endif()

if(WITH_IMAGE_OPENJPEG)
  add_definitions(-DWITH_OPENJPEG)
endif()

if(WITH_IMAGE_DDS)
  add_definitions(-DWITH_DDS)
endif()

if(WITH_IMAGE_CINEON)
  add_definitions(-DWITH_CINEON)
endif()

if(WITH_IMAGE_HDR)
  add_definitions(-DWITH_HDR)
endif()

if(WITH_IMAGE_WEBP)
  add_definitions(-DWITH_WEBP)
endif()

if(WITH_FREESTYLE)
  add_definitions(-DWITH_FREESTYLE)
endif()

ixam_add_lib(bf_editor_space_file "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h dna_type_offsets.h
add_dependencies(bf_editor_space_file bf_rna)
