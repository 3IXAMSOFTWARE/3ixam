

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ValueNode
 * \ingroup Node
 */
class ValueNode : public Node {
 public:
  ValueNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
