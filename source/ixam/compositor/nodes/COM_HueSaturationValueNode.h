

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief HueSaturationValueNode
 * \ingroup Node
 */
class HueSaturationValueNode : public Node {
 public:
  HueSaturationValueNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
