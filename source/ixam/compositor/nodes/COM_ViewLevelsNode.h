

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ViewLevelsNode
 * \ingroup Node
 */
class ViewLevelsNode : public Node {
 public:
  ViewLevelsNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor