/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2012 Blender Foundation. */


#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ConvertAlphaNode
 * \ingroup Node
 */
class ConvertAlphaNode : public Node {
 public:
  ConvertAlphaNode(bNode *editor_node) : Node(editor_node)
  {
  }
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
