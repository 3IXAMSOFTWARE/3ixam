

/** \file
 * \ingroup gpu
 */

#include "vk_batch.hh"

namespace ixam::gpu {

void VKBatch::draw(int /*v_first*/, int /*v_count*/, int /*i_first*/, int /*i_count*/)
{
}

void VKBatch::draw_indirect(GPUStorageBuf * /*indirect_buf*/, intptr_t /*offset*/)
{
}

void VKBatch::multi_draw_indirect(GPUStorageBuf * /*indirect_buf*/,
                                  int /*count*/,
                                  intptr_t /*offset*/,
                                  intptr_t /*stride*/)
{
}

}  // namespace ixam::gpu