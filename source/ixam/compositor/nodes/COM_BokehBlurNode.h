/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2011 Blender Foundation. */


#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief BokehBlurNode
 * \ingroup Node
 */
class BokehBlurNode : public Node {
 public:
  BokehBlurNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
