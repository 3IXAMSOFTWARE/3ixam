

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ChannelMatteNode
 * \ingroup Node
 */
class ChannelMatteNode : public Node {
 public:
  ChannelMatteNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor