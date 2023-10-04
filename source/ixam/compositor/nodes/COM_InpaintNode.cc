

#include "COM_InpaintNode.h"
#include "COM_InpaintOperation.h"

namespace ixam::compositor {

InpaintNode::InpaintNode(bNode *editor_node) : Node(editor_node)
{
  /* pass */
}

void InpaintNode::convert_to_operations(NodeConverter &converter,
                                        const CompositorContext & /*context*/) const
{

  const bNode *editor_node = this->get_bnode();

  /* if (editor_node->custom1 == CMP_NODE_INPAINT_SIMPLE) { */
  if (true) {
    InpaintSimpleOperation *operation = new InpaintSimpleOperation();
    operation->set_iterations(editor_node->custom2);
    converter.add_operation(operation);

    converter.map_input_socket(get_input_socket(0), operation->get_input_socket(0));
    converter.map_output_socket(get_output_socket(0), operation->get_output_socket(0));
  }
}

}  // namespace ixam::compositor
