

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief SunBeamsNode
 * \ingroup Node
 */
class SunBeamsNode : public Node {
 public:
  SunBeamsNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
