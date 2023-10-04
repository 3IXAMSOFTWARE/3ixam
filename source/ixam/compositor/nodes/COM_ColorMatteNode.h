

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ColorMatteNode
 * \ingroup Node
 */
class ColorMatteNode : public Node {
 public:
  ColorMatteNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
