

#pragma once

#include "COM_Node.h"
#include "DNA_node_types.h"

namespace ixam::compositor {

/**
 * \brief MixNode
 * \ingroup Node
 */
class MixNode : public Node {
 public:
  MixNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
