

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief TonemapNode
 * \ingroup Node
 */
class TonemapNode : public Node {
 public:
  TonemapNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
