

#pragma once

#include "COM_Node.h"
#include "DNA_node_types.h"

namespace ixam::compositor {

/**
 * \brief Stabilize2dNode
 * \ingroup Node
 */
class Stabilize2dNode : public Node {
 public:
  Stabilize2dNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
