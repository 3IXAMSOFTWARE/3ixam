

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief HueSaturationValueCorrectNode
 * \ingroup Node
 */
class HueSaturationValueCorrectNode : public Node {
 public:
  HueSaturationValueCorrectNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
