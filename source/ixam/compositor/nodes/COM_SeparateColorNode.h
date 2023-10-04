

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

class SeparateColorNode : public Node {
 public:
  SeparateColorNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
