

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief FilterNode
 * \ingroup Node
 */
class FilterNode : public Node {
 public:
  FilterNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
