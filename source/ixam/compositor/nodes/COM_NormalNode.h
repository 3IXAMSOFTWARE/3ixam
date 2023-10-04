

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief NormalNode
 * \ingroup Node
 */
class NormalNode : public Node {
 public:
  NormalNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
