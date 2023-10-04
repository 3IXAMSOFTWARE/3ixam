

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief RotateNode
 * \ingroup Node
 */
class RotateNode : public Node {
 public:
  RotateNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
