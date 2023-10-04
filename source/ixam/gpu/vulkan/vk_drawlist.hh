

/** \file
 * \ingroup gpu
 */

#pragma once

#include "gpu_drawlist_private.hh"

namespace ixam::gpu {

class VKDrawList : public DrawList {
 public:
  void append(GPUBatch *batch, int i_first, int i_count) override;
  void submit() override;
};

}  // namespace ixam::gpu