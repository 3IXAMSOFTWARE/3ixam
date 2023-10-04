

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief CropNode
 * \ingroup Node
 */
class CropNode : public Node {
 public:
  CropNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
