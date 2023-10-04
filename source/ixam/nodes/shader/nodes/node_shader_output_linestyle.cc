/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2005 Ixam Foundation. All rights reserved. */

#include "node_shader_util.hh"

#include "UI_interface.h"
#include "UI_resources.h"

namespace ixam::nodes::node_shader_output_linestyle_cc {

static void node_declare(NodeDeclarationBuilder &b)
{
  b.add_input<decl::Color>(N_("Color")).default_value({1.0f, 0.0f, 1.0f, 1.0f});
  b.add_input<decl::Float>(N_("Color Fac"))
      .default_value(1.0f)
      .min(0.0f)
      .max(1.0f)
      .subtype(PROP_FACTOR);
  b.add_input<decl::Float>(N_("Alpha"))
      .default_value(1.0f)
      .min(0.0f)
      .max(1.0f)
      .subtype(PROP_FACTOR);
  b.add_input<decl::Float>(N_("Alpha Fac"))
      .default_value(1.0f)
      .min(0.0f)
      .max(1.0f)
      .subtype(PROP_FACTOR);
}

static void node_buts_output_linestyle(uiLayout *layout, bContext * /*C*/, PointerRNA *ptr)
{
  uiLayout *row, *col;

  col = uiLayoutColumn(layout, false);
  row = uiLayoutRow(col, true);
  uiItemL(row, IFACE_("Blend Mode"), ICON_NONE, UI_BSHAPE_ROUNDBOX);
  uiItemR(row, ptr, "blend_type", UI_ITEM_R_SPLIT_EMPTY_NAME, "", ICON_NONE);
  uiItemS_ex(row, 3.4f, UI_BSHAPE_ROUNDBOX);

  row = uiLayoutRow(col, true);
  uiItemL(row, IFACE_("Clamp"), ICON_NONE, UI_BSHAPE_ROUNDBOX);
  uiItemR(row, ptr, "use_clamp", UI_ITEM_R_SPLIT_EMPTY_NAME, "", ICON_NONE);
}

}  // namespace ixam::nodes::node_shader_output_linestyle_cc

/* node type definition */
void register_node_type_sh_output_linestyle()
{
  namespace file_ns = ixam::nodes::node_shader_output_linestyle_cc;

  static bNodeType ntype;

  sh_node_type_base(&ntype, SH_NODE_OUTPUT_LINESTYLE, "Line Style Output", NODE_CLASS_OUTPUT);
  ntype.declare = file_ns::node_declare;
  ntype.draw_buttons = file_ns::node_buts_output_linestyle;
  ntype.no_muting = true;

  nodeRegisterType(&ntype);
}
