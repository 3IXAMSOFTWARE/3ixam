/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2022 Blender Foundation. All rights reserved. */


/** \file
 * \ingroup gpu
 */

#include "vk_context.hh"

namespace ixam::gpu {

void VKContext::activate()
{
}

void VKContext::deactivate()
{
}

void VKContext::begin_frame()
{
}

void VKContext::end_frame()
{
}

void VKContext::flush()
{
}

void VKContext::finish()
{
}

void VKContext::memory_statistics_get(int * /*total_mem*/, int * /*free_mem*/)
{
}

void VKContext::debug_group_begin(const char *, int)
{
}

void VKContext::debug_group_end()
{
}

}  // namespace ixam::gpu