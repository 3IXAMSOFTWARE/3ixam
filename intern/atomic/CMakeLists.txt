

set(INC
  .
)

set(INC_SYS
)

if(WITH_GTESTS)
  set(TEST_SRC
    tests/atomic_test.cc
  )
  set(TEST_INC
  )
  set(TEST_LIB
  )
  include(GTestTesting)
  ixam_add_test_executable(atomic "${TEST_SRC}" "${INC};${TEST_INC}" "${INC_SYS}" "${LIB};${TEST_LIB}")
endif()
