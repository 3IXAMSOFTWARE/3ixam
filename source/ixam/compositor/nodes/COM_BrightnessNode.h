

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief BrightnessNode
 * \ingroup Node
 */
class BrightnessNode : public Node {
 public:
  BrightnessNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
