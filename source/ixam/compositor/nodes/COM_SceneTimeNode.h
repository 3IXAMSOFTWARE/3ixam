

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief SceneTimeNode
 * \ingroup Node
 */
class SceneTimeNode : public Node {
 public:
  SceneTimeNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
