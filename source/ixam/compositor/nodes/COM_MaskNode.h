

#pragma once

#include "COM_Node.h"
#include "DNA_node_types.h"

namespace ixam::compositor {

/**
 * \brief MaskNode
 * \ingroup Node
 */
class MaskNode : public Node {
 public:
  MaskNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor