/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2022 Blender Foundation. All rights reserved. */


/** \file
 * \ingroup gpu
 */

#pragma once

#include "gpu_uniform_buffer_private.hh"

namespace ixam::gpu {

class VKUniformBuffer : public UniformBuf {
 public:
  VKUniformBuffer(int size, const char *name) : UniformBuf(size, name)
  {
  }

  void update(const void *data) override;
  void bind(int slot) override;
  void unbind() override;
};

}  // namespace ixam::gpu