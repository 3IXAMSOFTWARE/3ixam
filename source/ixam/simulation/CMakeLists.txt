
set(INC
  .
  intern
  ../ixamkernel
  ../ixamlib
  ../depsgraph
  ../functions
  ../imbuf
  ../makesdna
  ../makesrna
  ../nodes
  ../../../intern/guardedalloc
)

set(INC_SYS
  ${EIGEN3_INCLUDE_DIRS}
)

set(SRC
  intern/SIM_mass_spring.cpp
  intern/hair_volume.cpp
  intern/implicit_ixam.c
  intern/implicit_eigen.cpp

  intern/ConstrainedConjugateGradient.h
  intern/eigen_utils.h
  intern/implicit.h

  SIM_mass_spring.h
)

set(LIB
  bf_ixamkernel
)

if(WITH_OPENMP_STATIC)
  list(APPEND LIB
    ${OpenMP_LIBRARIES}
  )
endif()

ixam_add_lib(bf_simulation "${SRC}" "${INC}" "${INC_SYS}" "${LIB}")
