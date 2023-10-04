

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ExposureNode
 * \ingroup Node
 */
class ExposureNode : public Node {
 public:
  ExposureNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
