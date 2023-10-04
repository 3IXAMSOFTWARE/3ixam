

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DoubleEdgeMaskNode
 * \ingroup Node
 */
class DoubleEdgeMaskNode : public Node {
 public:
  DoubleEdgeMaskNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
