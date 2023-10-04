

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ColorCorrectionNode
 * \ingroup Node
 */
class ColorCorrectionNode : public Node {
 public:
  ColorCorrectionNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
