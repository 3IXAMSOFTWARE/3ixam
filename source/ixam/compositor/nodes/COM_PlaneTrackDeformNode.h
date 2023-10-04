

#pragma once

#include "COM_Node.h"

#include "DNA_movieclip_types.h"
#include "DNA_node_types.h"

namespace ixam::compositor {

/**
 * \brief PlaneTrackDeformNode
 * \ingroup Node
 */
class PlaneTrackDeformNode : public Node {
 public:
  PlaneTrackDeformNode(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;
};

}  // namespace ixam::compositor