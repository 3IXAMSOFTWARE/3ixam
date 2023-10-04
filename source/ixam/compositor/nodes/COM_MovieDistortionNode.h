

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief MovieDistortionNode
 * \ingroup Node
 */
class MovieDistortionNode : public Node {
 public:
  MovieDistortionNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
