

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ColorCurveNode
 * \ingroup Node
 */
class ColorCurveNode : public Node {
 public:
  ColorCurveNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
