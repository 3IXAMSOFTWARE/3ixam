
set(INC
  ../include
  ../../ixamfont
  ../../ixamkernel
  ../../ixamlib
  ../../ixamloader
  ../../ixamtranslation
  ../../compositor
  ../../depsgraph
  ../../draw
  ../../functions
  ../../gpu
  ../../imbuf
  ../../makesdna
  ../../makesrna
  ../../nodes
  ../../render
  ../../windowmanager
  ../../../../intern/guardedalloc

  # dna_type_offsets.h
  ${CMAKE_CURRENT_BINARY_DIR}/../../makesdna/intern
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)


set(SRC
  add_node_search_matpro.cc
  add_menu_assets_matpro.cc
  drawnode_matpro.cc
  link_drag_search_matpro.cc
  node_add_matpro.cc
  node_context_path_matpro.cc
  node_draw_matpro.cc
  node_edit_matpro.cc
  node_geometry_attribute_search_matpro.cc
  node_gizmo_matpro.cc
  node_group_matpro.cc
  node_ops_matpro.cc
  node_relationships_matpro.cc
  node_select_matpro.cc
  node_templates_matpro.cc
  node_view_matpro.cc
  space_matpro.cc

  matpro_intern.hh
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
  bf_editor_screen
)

if(WITH_COMPOSITOR_CPU)
  add_definitions(-DWITH_COMPOSITOR_CPU)
endif()

if(WITH_OPENIMAGEDENOISE)
  add_definitions(-DWITH_OPENIMAGEDENOISE)
endif()

if(WITH_OPENSUBDIV)
  add_definitions(-DWITH_OPENSUBDIV)
endif()

if(WITH_TBB)
  add_definitions(-DWITH_TBB)
  if(WIN32)
    # TBB includes Windows.h which will define min/max macros
    # that will collide with the stl versions.
    add_definitions(-DNOMINMAX)
  endif()
  list(APPEND INC_SYS
    ${TBB_INCLUDE_DIRS}
  )

  list(APPEND LIB
    ${TBB_LIBRARIES}
  )
endif()

ixam_add_lib(bf_editor_space_matpro "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h dna_type_offsets.h
add_dependencies(bf_editor_space_matpro bf_rna)
