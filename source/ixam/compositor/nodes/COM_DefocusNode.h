

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DefocusNode
 * \ingroup Node
 */
class DefocusNode : public Node {
 public:
  DefocusNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
