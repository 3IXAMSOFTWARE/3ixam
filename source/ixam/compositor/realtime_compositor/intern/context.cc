/* SPDX-License-Identifier: GPL-2.0-or-later */

#include "COM_context.hh"
#include "COM_static_shader_manager.hh"
#include "COM_texture_pool.hh"

namespace ixam::realtime_compositor {

Context::Context(TexturePool &texture_pool) : texture_pool_(texture_pool)
{
}

int Context::get_frame_number() const
{
  return get_scene()->r.cfra;
}

float Context::get_time() const
{
  const float frame_number = float(get_frame_number());
  const float frame_rate = float(get_scene()->r.frs_sec) / float(get_scene()->r.frs_sec_base);
  return frame_number / frame_rate;
}

TexturePool &Context::texture_pool()
{
  return texture_pool_;
}

StaticShaderManager &Context::shader_manager()
{
  return shader_manager_;
}

}  // namespace ixam::realtime_compositor
