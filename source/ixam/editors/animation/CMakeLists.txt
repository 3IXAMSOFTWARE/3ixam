
set(INC
  ../include
  ../../ixamkernel
  ../../ixamlib
  ../../ixamtranslation
  ../../depsgraph
  ../../gpu
  ../../makesdna
  ../../makesrna
  ../../sequencer
  ../../windowmanager
  ../../../../intern/clog
  ../../../../intern/guardedalloc
  # RNA_prototypes.h
  ${CMAKE_BINARY_DIR}/source/ixam/makesrna
)


set(SRC
  anim_channels_defines.c
  anim_channels_edit.c
  anim_deps.c
  anim_draw.c
  anim_filter.c
  anim_ipo_utils.c
  anim_markers.c
  anim_motion_paths.c
  anim_ops.c
  drivers.c
  fmodifier_ui.c
  keyframes_draw.c
  keyframes_edit.c
  keyframes_general.c
  keyframes_keylist.cc
  keyframing.c
  keyingsets.c
  time_scrub_ui.c

  anim_intern.h
)

set(LIB
  bf_ixamkernel
  bf_ixamlib
)

if(WITH_PYTHON)
  add_definitions(-DWITH_PYTHON)
endif()


ixam_add_lib(bf_editor_animation "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")

# RNA_prototypes.h
add_dependencies(bf_editor_animation bf_rna)

if(WITH_GTESTS)
  set(TEST_SRC
    keyframes_keylist_test.cc
  )
  set(TEST_INC
  )
  set(TEST_LIB
  )
  include(GTestTesting)
  ixam_add_test_lib(bf_editor_animation_tests "${TEST_SRC}" "${INC};${TEST_INC}" "${INC_SYS}" "${LIB};${TEST_LIB}")
endif()
