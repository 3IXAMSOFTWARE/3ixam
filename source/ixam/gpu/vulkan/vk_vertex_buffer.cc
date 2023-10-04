

/** \file
 * \ingroup gpu
 */

#include "vk_vertex_buffer.hh"

namespace ixam::gpu {

void VKVertexBuffer::bind_as_ssbo(uint /*binding*/)
{
}

void VKVertexBuffer::bind_as_texture(uint /*binding*/)
{
}

void VKVertexBuffer::wrap_handle(uint64_t /*handle*/)
{
}

void VKVertexBuffer::update_sub(uint /*start*/, uint /*len*/, const void * /*data*/)
{
}

const void *VKVertexBuffer::read() const
{
  return nullptr;
}

void *VKVertexBuffer::unmap(const void * /*mapped_data*/) const
{
  return nullptr;
}

void VKVertexBuffer::acquire_data()
{
}

void VKVertexBuffer::resize_data()
{
}

void VKVertexBuffer::release_data()
{
}

void VKVertexBuffer::upload_data()
{
}

void VKVertexBuffer::duplicate_data(VertBuf * /*dst*/)
{
}

}  // namespace ixam::gpu