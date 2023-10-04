

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief IDMaskNode
 * \ingroup Node
 */
class IDMaskNode : public Node {
 public:
  IDMaskNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
