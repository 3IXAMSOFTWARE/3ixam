

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DespeckleNode
 * \ingroup Node
 */
class DespeckleNode : public Node {
 public:
  DespeckleNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
