

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief AlphaOverNode
 * \ingroup Node
 */
class AlphaOverNode : public Node {
 public:
  AlphaOverNode(bNode *editor_node) : Node(editor_node)
  {
  }
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
