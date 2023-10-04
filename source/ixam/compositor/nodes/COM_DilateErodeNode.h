

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

/**
 * \brief DilateErodeNode
 * \ingroup Node
 */
class DilateErodeNode : public Node {
  /** only used for blurring alpha, since the dilate/erode node doesn't have this. */
  NodeBlurData alpha_blur_;

 public:
  DilateErodeNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
