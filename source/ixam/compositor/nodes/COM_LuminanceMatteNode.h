

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief LuminanceMatteNode
 * \ingroup Node
 */
class LuminanceMatteNode : public Node {
 public:
  LuminanceMatteNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
