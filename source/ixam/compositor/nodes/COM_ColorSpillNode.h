

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ColorSpillNode
 * \ingroup Node
 */
class ColorSpillNode : public Node {
 public:
  ColorSpillNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor