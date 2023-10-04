

/** \file
 * \ingroup gpu
 */

#include "vk_index_buffer.hh"

namespace ixam::gpu {

void VKIndexBuffer::upload_data()
{
}

void VKIndexBuffer::bind_as_ssbo(uint /*binding*/)
{
}

const uint32_t *VKIndexBuffer::read() const
{
  return 0;
}

void VKIndexBuffer::update_sub(uint /*start*/, uint /*len*/, const void * /*data*/)
{
}

void VKIndexBuffer::strip_restart_indices()
{
}

}  // namespace ixam::gpu