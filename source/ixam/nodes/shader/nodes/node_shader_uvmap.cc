/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2005 Ixam Foundation. All rights reserved. */

#include "node_shader_util.hh"

#include "BKE_context.h"

#include "DNA_customdata_types.h"

#include "UI_interface.h"
#include "UI_resources.h"

namespace ixam::nodes::node_shader_uvmap_cc {

static void node_declare(NodeDeclarationBuilder &b)
{
  b.add_output<decl::Vector>(N_("UV"));
}

static void node_shader_buts_uvmap(uiLayout *layout, bContext *C, PointerRNA *ptr)
{
  uiLayout *row = uiLayoutRow(layout, true);
  uiItemL(row, IFACE_("From Instancer"), ICON_NONE, UI_BSHAPE_ROUNDBOX);  
  uiItemR(row, ptr, "from_instancer", UI_ITEM_R_SPLIT_EMPTY_NAME, "", 0);

  if (!RNA_boolean_get(ptr, "from_instancer")) {
    PointerRNA obptr = CTX_data_pointer_get(C, "active_object");

    if (obptr.data && RNA_enum_get(&obptr, "type") == OB_MESH) {
      PointerRNA dataptr = RNA_pointer_get(&obptr, "data");
      row = uiLayoutRow(layout, true);
      uiItemL(row, IFACE_("UV Map"), ICON_NONE, UI_BSHAPE_ROUNDBOX); 
      uiItemPointerR(row, ptr, "uv_map", &dataptr, "uv_layers", "", ICON_NONE);
    }
  }
}

static void node_shader_init_uvmap(bNodeTree * /*ntree*/, bNode *node)
{
  NodeShaderUVMap *attr = MEM_cnew<NodeShaderUVMap>("NodeShaderUVMap");
  node->storage = attr;
}

static int node_shader_gpu_uvmap(GPUMaterial *mat,
                                 bNode *node,
                                 bNodeExecData * /*execdata*/,
                                 GPUNodeStack *in,
                                 GPUNodeStack *out)
{
  NodeShaderUVMap *attr = static_cast<NodeShaderUVMap *>(node->storage);

  /* NOTE: using CD_AUTO_FROM_NAME instead of CD_MTFACE as geometry nodes may overwrite data which
   * will also change the eCustomDataType. This will also make EEVEE and Cycles consistent. See
   * T93179. */
  GPUNodeLink *mtface = GPU_attribute(mat, CD_AUTO_FROM_NAME, attr->uv_map);

  GPU_stack_link(mat, node, "node_uvmap", in, out, mtface);

  node_shader_gpu_bump_tex_coord(mat, node, &out[0].link);

  return 1;
}

}  // namespace ixam::nodes::node_shader_uvmap_cc

/* node type definition */
void register_node_type_sh_uvmap()
{
  namespace file_ns = ixam::nodes::node_shader_uvmap_cc;

  static bNodeType ntype;

  sh_node_type_base(&ntype, SH_NODE_UVMAP, "UV Map", NODE_CLASS_INPUT);
  ntype.declare = file_ns::node_declare;
  ntype.draw_buttons = file_ns::node_shader_buts_uvmap;
  node_type_size_preset(&ntype, NODE_SIZE_MIDDLE);
  node_type_init(&ntype, file_ns::node_shader_init_uvmap);
  node_type_storage(
      &ntype, "NodeShaderUVMap", node_free_standard_storage, node_copy_standard_storage);
  node_type_gpu(&ntype, file_ns::node_shader_gpu_uvmap);

  nodeRegisterType(&ntype);
}
