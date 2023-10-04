

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DirectionalBlurNode
 * \ingroup Node
 */
class DirectionalBlurNode : public Node {
 public:
  DirectionalBlurNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
