

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief GammaNode
 * \ingroup Node
 */
class GammaNode : public Node {
 public:
  GammaNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
