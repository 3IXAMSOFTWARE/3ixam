

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief InpaintNode
 * \ingroup Node
 */
class InpaintNode : public Node {
 public:
  InpaintNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
