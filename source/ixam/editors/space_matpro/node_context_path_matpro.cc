

/** \file
 * \ingroup spnode
 * \brief Node breadcrumbs drawing
 */

#include "BLI_vector.hh"

#include "DNA_node_types.h"

#include "BKE_context.h"
#include "BKE_material.h"
#include "BKE_modifier.h"
#include "BKE_object.h"

#include "BKE_screen.h"

#include "RNA_access.h"
#include "RNA_prototypes.h"

#include "ED_screen.h"

#include "UI_interface.h"
#include "UI_interface.hh"
#include "UI_resources.h"

#include "matpro_intern.hh"

struct Material;

namespace ixam::ed::space_matpro {

static void context_path_add_object_data(Vector<ui::ContextPathItem> &path, Object &object)
{
  if (!object.data) {
    return;
  }
  if (object.type == OB_MESH) {
    ui::context_path_add_generic(path, RNA_Mesh, object.data);
  }
  else if (object.type == OB_CURVES) {
    ui::context_path_add_generic(path, RNA_Curves, object.data);
  }
  else if (object.type == OB_LAMP) {
    ui::context_path_add_generic(path, RNA_Light, object.data);
  }
  else if (ELEM(object.type, OB_CURVES_LEGACY, OB_FONT, OB_SURF)) {
    ui::context_path_add_generic(path, RNA_Curve, object.data);
  }
}

static void context_path_add_node_tree_and_node_groups(const SpaceMatPro &smatpro,
                                                       Vector<ui::ContextPathItem> &path,
                                                       const bool skip_base = false)
{
  Vector<const bNodeTreePath *> tree_path = smatpro.treepath;
  for (const bNodeTreePath *path_item : tree_path.as_span().drop_front(int(skip_base))) {
    ui::context_path_add_generic(path, RNA_NodeTree, path_item->nodetree, ICON_NODETREE);
  }
}

static void get_context_path_node_shader(const bContext &C,
                                         SpaceMatPro &smatpro,
                                         Vector<ui::ContextPathItem> &path)
{
  if (smatpro.flag & SNODE_PIN) {
    if (smatpro.shaderfrom == SNODE_SHADER_WORLD) {
      Scene *scene = CTX_data_scene(&C);
      ui::context_path_add_generic(path, RNA_Scene, scene);
      if (scene != nullptr) {
        ui::context_path_add_generic(path, RNA_World, scene->world);
      }
      /* Skip the base node tree here, because the world contains a node tree already. */
      context_path_add_node_tree_and_node_groups(smatpro, path, true);
    }
    else {
      context_path_add_node_tree_and_node_groups(smatpro, path);
    }
  }
  else {
    Object *object = CTX_data_active_object(&C);
    if (smatpro.shaderfrom == SNODE_SHADER_OBJECT && object != nullptr) {
      ui::context_path_add_generic(path, RNA_Object, object);
      if (!(object->matbits && object->matbits[object->actcol - 1])) {
        context_path_add_object_data(path, *object);
      }
      Material *material = BKE_object_material_get(object, object->actcol);
      ui::context_path_add_generic(path, RNA_Material, material);
    }
    else if (smatpro.shaderfrom == SNODE_SHADER_WORLD) {
      Scene *scene = CTX_data_scene(&C);
      ui::context_path_add_generic(path, RNA_Scene, scene);
      if (scene != nullptr) {
        ui::context_path_add_generic(path, RNA_World, scene->world);
      }
    }
#ifdef WITH_FREESTYLE
    else if (smatpro.shaderfrom == SNODE_SHADER_LINESTYLE) {
      ViewLayer *viewlayer = CTX_data_view_layer(&C);
      FreestyleLineStyle *linestyle = BKE_linestyle_active_from_view_layer(viewlayer);
      ui::context_path_add_generic(path, RNA_ViewLayer, viewlayer);
      Material *mat = BKE_object_material_get(object, object->actcol);
      ui::context_path_add_generic(path, RNA_Material, mat);
    }
#endif
    context_path_add_node_tree_and_node_groups(smatpro, path, true);
  }
}

static void get_context_path_node_compositor(const bContext &C,
                                             SpaceMatPro &smatpro,
                                             Vector<ui::ContextPathItem> &path)
{
  if (smatpro.flag & SNODE_PIN) {
    context_path_add_node_tree_and_node_groups(smatpro, path);
  }
  else {
    Scene *scene = CTX_data_scene(&C);
    ui::context_path_add_generic(path, RNA_Scene, scene);
    context_path_add_node_tree_and_node_groups(smatpro, path);
  }
}

static void get_context_path_node_geometry(const bContext &C,
                                           SpaceMatPro &smatpro,
                                           Vector<ui::ContextPathItem> &path)
{
  if (smatpro.flag & SNODE_PIN) {
    context_path_add_node_tree_and_node_groups(smatpro, path);
  }
  else {
    Object *object = CTX_data_active_object(&C);
    ui::context_path_add_generic(path, RNA_Object, object);
    ModifierData *modifier = BKE_object_active_modifier(object);
    ui::context_path_add_generic(path, RNA_Modifier, modifier, ICON_GEOMETRY_NODES);
    context_path_add_node_tree_and_node_groups(smatpro, path);
  }
}

Vector<ui::ContextPathItem> context_path_for_space_matpro(const bContext &C)
{
  SpaceMatPro *smatpro = CTX_wm_space_matpro(&C);
  if (smatpro == nullptr) {
    return {};
  }

  Vector<ui::ContextPathItem> context_path;

  if (smatpro->edittree->type == NTREE_GEOMETRY) {
    get_context_path_node_geometry(C, *smatpro, context_path);
  }
  else if (smatpro->edittree->type == NTREE_SHADER) {
    get_context_path_node_shader(C, *smatpro, context_path);
  }
  else if (smatpro->edittree->type == NTREE_COMPOSIT) {
    get_context_path_node_compositor(C, *smatpro, context_path);
  }

  return context_path;
}

}  // namespace ixam::ed::space_matpro
