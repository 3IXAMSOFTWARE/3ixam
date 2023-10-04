

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief SeparateXYZNode
 * \ingroup Node
 */
class SeparateXYZNode : public Node {
 public:
  SeparateXYZNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
