

/** \file
 * \ingroup gpu
 */

#include "vk_vertex_buffer.hh"

#include "vk_storage_buffer.hh"

namespace ixam::gpu {

void VKStorageBuffer::update(const void * /*data*/)
{
}

void VKStorageBuffer::bind(int /*slot*/)
{
}

void VKStorageBuffer::unbind()
{
}

void VKStorageBuffer::clear(eGPUTextureFormat /* internal_format*/,
                            eGPUDataFormat /*data_format*/,
                            void * /*data*/)
{
}
void VKStorageBuffer::copy_sub(VertBuf * /*src*/,
                               uint /*dst_offset*/,
                               uint /*src_offset*/,
                               uint /*copy_size*/)
{
}

void VKStorageBuffer::read(void * /*data*/)
{
}

}  // namespace ixam::gpu