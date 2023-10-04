

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief InvertNode
 * \ingroup Node
 */
class InvertNode : public Node {
 public:
  InvertNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
