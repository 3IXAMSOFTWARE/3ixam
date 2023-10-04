

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief FlipNode
 * \ingroup Node
 */
class FlipNode : public Node {
 public:
  FlipNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
