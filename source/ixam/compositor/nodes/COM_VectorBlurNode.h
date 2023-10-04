

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief VectorBlurNode
 * \ingroup Node
 */
class VectorBlurNode : public Node {
 public:
  VectorBlurNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor