/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2005 Ixam Foundation. All rights reserved. */

#include "node_shader_util.hh"

#include "UI_interface.h"
#include "UI_resources.h"

namespace ixam::nodes::node_shader_bsdf_toon_cc {

static void node_declare(NodeDeclarationBuilder &b)
{
  b.add_input<decl::Color>(N_("Color")).default_value({0.8f, 0.8f, 0.8f, 1.0f});
  b.add_input<decl::Float>(N_("Size"))
      .default_value(0.5f)
      .min(0.0f)
      .max(1.0f)
      .subtype(PROP_FACTOR);
  b.add_input<decl::Float>(N_("Smooth"))
      .default_value(0.0f)
      .min(0.0f)
      .max(1.0f)
      .subtype(PROP_FACTOR);
  b.add_input<decl::Vector>(N_("Normal")).hide_value();
  b.add_input<decl::Float>(N_("Weight")).unavailable();
  b.add_output<decl::Shader>(N_("BSDF"));
}

static void node_shader_buts_toon(uiLayout *layout, bContext * /*C*/, PointerRNA *ptr)
{
  uiLayout *row = uiLayoutRow(layout, true);
  uiItemL(row, IFACE_("Component"), ICON_NONE, UI_BSHAPE_ROUNDBOX);
  uiItemR(row, ptr, "component", UI_ITEM_R_SPLIT_EMPTY_NAME, "", ICON_NONE);
  uiItemS_ex(row, 3.4f, UI_BSHAPE_ROUNDBOX);
}

static int node_shader_gpu_bsdf_toon(GPUMaterial *mat,
                                     bNode *node,
                                     bNodeExecData * /*execdata*/,
                                     GPUNodeStack *in,
                                     GPUNodeStack *out)
{
  if (!in[3].link) {
    GPU_link(mat, "world_normals_get", &in[3].link);
  }

  GPU_material_flag_set(mat, GPU_MATFLAG_DIFFUSE);

  return GPU_stack_link(mat, node, "node_bsdf_toon", in, out);
}

}  // namespace ixam::nodes::node_shader_bsdf_toon_cc

/* node type definition */
void register_node_type_sh_bsdf_toon()
{
  namespace file_ns = ixam::nodes::node_shader_bsdf_toon_cc;

  static bNodeType ntype;

  sh_node_type_base(&ntype, SH_NODE_BSDF_TOON, "Toon", NODE_CLASS_SHADER);
  ntype.declare = file_ns::node_declare;
  ntype.draw_buttons = file_ns::node_shader_buts_toon;
  node_type_size_preset(&ntype, NODE_SIZE_MIDDLE);
  node_type_gpu(&ntype, file_ns::node_shader_gpu_bsdf_toon);

  nodeRegisterType(&ntype);
}
