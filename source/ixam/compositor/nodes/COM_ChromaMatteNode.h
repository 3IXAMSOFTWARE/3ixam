

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief ChromaMatteNode
 * \ingroup Node
 */
class ChromaMatteNode : public Node {
 public:
  ChromaMatteNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
