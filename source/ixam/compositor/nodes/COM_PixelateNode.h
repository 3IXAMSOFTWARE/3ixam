

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief PixelateNode
 * \ingroup Node
 */
class PixelateNode : public Node {
 public:
  PixelateNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
