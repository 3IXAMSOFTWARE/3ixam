

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief MathNode
 * \ingroup Node
 */
class MathNode : public Node {
 public:
  MathNode(bNode *editor_node) : Node(editor_node)
  {
  }
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
