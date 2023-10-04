

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ScaleNode
 * \ingroup Node
 */
class ScaleNode : public Node {
 public:
  ScaleNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
