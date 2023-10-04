

#include "COM_BokehImageNode.h"
#include "COM_BokehImageOperation.h"

namespace ixam::compositor {

BokehImageNode::BokehImageNode(bNode *editor_node) : Node(editor_node)
{
  /* pass */
}

void BokehImageNode::convert_to_operations(NodeConverter &converter,
                                           const CompositorContext & /*context*/) const
{
  BokehImageOperation *operation = new BokehImageOperation();
  operation->set_data((const NodeBokehImage *)this->get_bnode()->storage);

  converter.add_operation(operation);
  converter.map_output_socket(get_output_socket(0), operation->get_output_socket(0));

  converter.add_preview(operation->get_output_socket(0));
}

}  // namespace ixam::compositor
