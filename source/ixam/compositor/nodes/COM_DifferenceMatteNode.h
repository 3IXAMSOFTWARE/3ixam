

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DifferenceMatteNode
 * \ingroup Node
 */
class DifferenceMatteNode : public Node {
 public:
  DifferenceMatteNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
