

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief PosterizeNode
 * \ingroup Node
 */
class PosterizeNode : public Node {
 public:
  PosterizeNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
