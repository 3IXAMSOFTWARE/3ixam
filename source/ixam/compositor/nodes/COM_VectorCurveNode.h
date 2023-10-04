

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief VectorCurveNode
 * \ingroup Node
 */
class VectorCurveNode : public Node {
 public:
  VectorCurveNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
