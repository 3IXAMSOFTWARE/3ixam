

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief BokehImageNode
 * \ingroup Node
 */
class BokehImageNode : public Node {
 public:
  BokehImageNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
