

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DenoiseNode
 * \ingroup Node
 */
class DenoiseNode : public Node {
 public:
  DenoiseNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
