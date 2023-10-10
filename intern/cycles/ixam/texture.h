/* SPDX-License-Identifier: Apache-2.0
 * Copyright 2011-2022 Blender Foundation */


#ifndef __IXAM_TEXTURE_H__
#define __IXAM_TEXTURE_H__

#include "ixam/sync.h"
#include <stdlib.h>

CCL_NAMESPACE_BEGIN

void point_density_texture_space(BL::Depsgraph &b_depsgraph,
                                 BL::ShaderNodeTexPointDensity &b_point_density_node,
                                 float3 &loc,
                                 float3 &size);

CCL_NAMESPACE_END

#endif /* __IXAM_TEXTURE_H__ */
