/* SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

#include "DNA_node_types.h"

struct Main;
struct Material;

namespace ixam::io::obj {

struct MTLMaterial;

bNodeTree *create_mtl_node_tree(Main *bmain,
                                const MTLMaterial &mtl_mat,
                                Material *mat,
                                bool relative_paths);

}  // namespace ixam::io::obj
