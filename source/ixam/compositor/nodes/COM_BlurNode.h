

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief BlurNode
 * \ingroup Node
 */
class BlurNode : public Node {
 public:
  BlurNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
