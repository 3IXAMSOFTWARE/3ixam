

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DistanceMatteNode
 * \ingroup Node
 */
class DistanceMatteNode : public Node {
 public:
  DistanceMatteNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
