

# Build Draco library.
add_subdirectory(draco)

# Build Draco-3IXAM bridging module.
set(SRC
  src/common.cpp
  src/common.h
  src/decoder.cpp
  src/decoder.h
  src/encoder.cpp
  src/encoder.h
)

set(INC
  draco/src
)

set(LIB
  draco
)

add_library(extern_draco SHARED "${SRC}")
target_include_directories(extern_draco PUBLIC "${INC}")
target_link_libraries(extern_draco PUBLIC "${LIB}")

ixam_source_group(extern_draco "${SRC}")
