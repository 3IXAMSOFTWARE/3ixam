

#pragma once

#include "COM_Node.h"

namespace ixam::compositor {

class CombineColorNodeLegacy : public Node {
 public:
  CombineColorNodeLegacy(bNode *editor_node);
  void convert_to_operations(NodeConverter &converter,
                             const CompositorContext &context) const override;

 protected:
  virtual NodeOperation *get_color_converter(const CompositorContext &context) const = 0;
};

class CombineRGBANode : public CombineColorNodeLegacy {
 public:
  CombineRGBANode(bNode *editor_node) : CombineColorNodeLegacy(editor_node)
  {
  }

  NodeOperation *get_color_converter(const CompositorContext &context) const override;
};

class CombineHSVANode : public CombineColorNodeLegacy {
 public:
  CombineHSVANode(bNode *editor_node) : CombineColorNodeLegacy(editor_node)
  {
  }

  NodeOperation *get_color_converter(const CompositorContext &context) const override;
};

class CombineYCCANode : public CombineColorNodeLegacy {
 public:
  CombineYCCANode(bNode *editor_node) : CombineColorNodeLegacy(editor_node)
  {
  }

  NodeOperation *get_color_converter(const CompositorContext &context) const override;
};

class CombineYUVANode : public CombineColorNodeLegacy {
 public:
  CombineYUVANode(bNode *editor_node) : CombineColorNodeLegacy(editor_node)
  {
  }

  NodeOperation *get_color_converter(const CompositorContext &context) const override;
};

}  // namespace ixam::compositor
