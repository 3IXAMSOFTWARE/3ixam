

#ifdef WITH_NANOVDB
#  include <nanovdb/NanoVDB.h>
#  include <nanovdb/util/SampleFromVoxels.h>
#endif

/* clang-format off */
struct ONEAPIKernelContext : public KernelGlobalsGPU {
  public:
#    include "kernel/device/oneapi/image.h"
  /* clang-format on */
