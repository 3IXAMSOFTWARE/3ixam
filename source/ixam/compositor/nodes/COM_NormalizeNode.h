

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief NormalizeNode
 * \ingroup Node
 */
class NormalizeNode : public Node {
 public:
  NormalizeNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
