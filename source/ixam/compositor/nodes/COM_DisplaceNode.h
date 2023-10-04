

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DisplaceNode
 * \ingroup Node
 */
class DisplaceNode : public Node {
 public:
  DisplaceNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
