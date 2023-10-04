
set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../bmesh
  ../../depsgraph
  ../../draw
  ../../gpu
  ../../imbuf
  ../../makesdna
  ../../makesrna
  ../../nodes
  ../../render
  ../../sequencer
  ../../windowmanager
  ../../../../intern/guardedalloc
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)

set(SRC
  render_internal.cc
  render_opengl.cc
  render_ops.cc
  render_preview.cc
  render_shading.cc
  render_update.cc
  render_view.cc

  render_intern.hh
)

set(LIB
)

if(WITH_HEADLESS)
  add_definitions(-DWITH_HEADLESS)
else()
  list(APPEND LIB
    bf_editor_datafiles
  )
endif()


if(WITH_FREESTYLE)
  list(APPEND INC
    ../../freestyle
  )
  add_definitions(-DWITH_FREESTYLE)
endif()

if(WITH_TBB)
  list(APPEND INC_SYS
    ${TBB_INCLUDE_DIRS}
  )
  add_definitions(-DWITH_TBB)
  if(WIN32)
    # TBB includes Windows.h which will define min/max macros
    # that will collide with the stl versions.
    add_definitions(-DNOMINMAX)
  endif()
endif()

ixam_add_lib(bf_editor_render "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h
add_dependencies(bf_editor_render bf_rna)
