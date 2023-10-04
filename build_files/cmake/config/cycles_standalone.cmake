
# only compile Cycles standalone, without 3IXAM
#
# Example usage:
#   cmake -C../ixam/build_files/cmake/config/cycles_standalone.cmake  ../ixam
#

# disable 3IXAM
set(WITH_IXAM             OFF  CACHE BOOL "" FORCE)
set(WITH_CYCLES_IXAM      OFF  CACHE BOOL "" FORCE)

# build Cycles
set(WITH_CYCLES_STANDALONE        ON CACHE BOOL "" FORCE)
set(WITH_CYCLES_STANDALONE_GUI    ON CACHE BOOL "" FORCE)
