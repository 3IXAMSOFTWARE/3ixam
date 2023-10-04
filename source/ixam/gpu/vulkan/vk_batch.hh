

/** \file
 * \ingroup gpu
 */

#pragma once

#include "gpu_batch_private.hh"

namespace ixam::gpu {

class VKBatch : public Batch {
 public:
  void draw(int v_first, int v_count, int i_first, int i_count) override;
  void draw_indirect(GPUStorageBuf *indirect_buf, intptr_t offset) override;
  void multi_draw_indirect(GPUStorageBuf *indirect_buf,
                           int count,
                           intptr_t offset,
                           intptr_t stride) override;
};

}  // namespace ixam::gpu