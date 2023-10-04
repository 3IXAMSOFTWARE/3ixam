/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2018 Ixam Foundation. All rights reserved. */

#include "node_shader_util.hh"

#include "UI_interface.h"
#include "UI_resources.h"

namespace ixam::nodes::node_shader_ies_light_cc {

static void node_declare(NodeDeclarationBuilder &b)
{
  b.add_input<decl::Vector>(N_("Vector")).hide_value();
  b.add_input<decl::Float>(N_("Strength")).default_value(1.0f).min(0.0f).max(1000000.0f);
  b.add_output<decl::Float>(N_("Fac"));
}

static void node_shader_buts_ies(uiLayout *layout, bContext * /*C*/, PointerRNA *ptr)
{
  uiLayout *row;

  row = uiLayoutRow(layout, false);
  uiItemR(row, ptr, "mode", UI_ITEM_R_SPLIT_EMPTY_NAME | UI_ITEM_R_EXPAND, nullptr, ICON_NONE);

  row = uiLayoutRow(layout, true);

  if (RNA_enum_get(ptr, "mode") == NODE_IES_INTERNAL) {
    uiItemL(row, IFACE_("Text"), ICON_NONE, UI_BSHAPE_ROUNDBOX);
    uiItemR(row, ptr, "ies", UI_ITEM_R_SPLIT_EMPTY_NAME, "", ICON_NONE);
    uiItemS_ex(row, 3.4f, UI_BSHAPE_ROUNDBOX);
  }
  else {
    uiItemL(row, IFACE_("File Path"), ICON_NONE, UI_BSHAPE_ROUNDBOX);
    uiItemR(row, ptr, "filepath", UI_ITEM_R_SPLIT_EMPTY_NAME, "", ICON_NONE);
    uiItemS_ex(row, 3.4f, UI_BSHAPE_ROUNDBOX);
  }
}

static void node_shader_init_tex_ies(bNodeTree * /*ntree*/, bNode *node)
{
  NodeShaderTexIES *tex = MEM_cnew<NodeShaderTexIES>("NodeShaderIESLight");
  node->storage = tex;
}

}  // namespace ixam::nodes::node_shader_ies_light_cc

/* node type definition */
void register_node_type_sh_tex_ies()
{
  namespace file_ns = ixam::nodes::node_shader_ies_light_cc;

  static bNodeType ntype;

  sh_node_type_base(&ntype, SH_NODE_TEX_IES, "IES Texture", NODE_CLASS_TEXTURE);
  ntype.declare = file_ns::node_declare;
  ntype.draw_buttons = file_ns::node_shader_buts_ies;
  node_type_init(&ntype, file_ns::node_shader_init_tex_ies);
  node_type_storage(
      &ntype, "NodeShaderTexIES", node_free_standard_storage, node_copy_standard_storage);

  nodeRegisterType(&ntype);
}
