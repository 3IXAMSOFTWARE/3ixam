

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief AntiAliasingNode
 * \ingroup Node
 */
class AntiAliasingNode : public Node {
 public:
  AntiAliasingNode(bNode *editor_node) : Node(editor_node)
  {
  }
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
