

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief EllipseMaskNode
 * \ingroup Node
 */
class EllipseMaskNode : public Node {
 public:
  EllipseMaskNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
