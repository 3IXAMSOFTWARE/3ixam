

/** \file
 * \ingroup gpu
 */

#include "vk_texture.hh"

namespace ixam::gpu {

void VKTexture::generate_mipmap()
{
}

void VKTexture::copy_to(Texture * /*tex*/)
{
}

void VKTexture::clear(eGPUDataFormat /*format*/, const void * /*data*/)
{
}

void VKTexture::swizzle_set(const char /*swizzle_mask*/[4])
{
}

void VKTexture::stencil_texture_mode_set(bool /*use_stencil*/)
{
}

void VKTexture::mip_range_set(int /*min*/, int /*max*/)
{
}

void *VKTexture::read(int /*mip*/, eGPUDataFormat /*format*/)
{
  return nullptr;
}

void VKTexture::update_sub(int /*mip*/,
                           int /*offset*/[3],
                           int /*extent*/[3],
                           eGPUDataFormat /*format*/,
                           const void * /*data*/)
{
}

/* TODO(fclem): Legacy. Should be removed at some point. */
uint VKTexture::gl_bindcode_get() const
{
  return 0;
}

bool VKTexture::init_internal()
{
  return false;
}

bool VKTexture::init_internal(GPUVertBuf * /*vbo*/)
{
  return false;
}

bool VKTexture::init_internal(const GPUTexture * /*src*/, int /*mip_offset*/, int /*layer_offset*/)
{
  return false;
}

}  // namespace ixam::gpu