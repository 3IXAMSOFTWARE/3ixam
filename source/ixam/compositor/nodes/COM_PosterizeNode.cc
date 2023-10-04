

#include "COM_PosterizeNode.h"
#include "COM_PosterizeOperation.h"

namespace ixam::compositor {

PosterizeNode::PosterizeNode(bNode *editor_node) : Node(editor_node)
{
  /* pass */
}

void PosterizeNode::convert_to_operations(NodeConverter &converter,
                                          const CompositorContext & /*context*/) const
{
  PosterizeOperation *operation = new PosterizeOperation();
  converter.add_operation(operation);

  converter.map_input_socket(get_input_socket(0), operation->get_input_socket(0));
  converter.map_input_socket(get_input_socket(1), operation->get_input_socket(1));
  converter.map_output_socket(get_output_socket(0), operation->get_output_socket(0));
}

}  // namespace ixam::compositor
