

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief MapUVNode
 * \ingroup Node
 */
class MapUVNode : public Node {
 public:
  MapUVNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
