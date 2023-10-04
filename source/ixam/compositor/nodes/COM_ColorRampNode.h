

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ColorRampNode
 * \ingroup Node
 */
class ColorRampNode : public Node {
 public:
  ColorRampNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
