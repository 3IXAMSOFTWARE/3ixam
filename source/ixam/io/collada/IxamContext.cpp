/* SPDX-License-Identifier: GPL-2.0-or-later */

#include <vector>

#include "IxamContext.h"
#include "ExportSettings.h"

#include "BKE_layer.h"
#include "BKE_scene.h"

#include "BLI_listbase.h"

bool bc_is_base_node(LinkNode *export_set, Object *ob, const Scene *scene, ViewLayer *view_layer)
{
  Object *root = bc_get_highest_exported_ancestor_or_self(export_set, ob, scene, view_layer);
  return (root == ob);
}

Object *bc_get_highest_exported_ancestor_or_self(LinkNode *export_set,
                                                 Object *ob,
                                                 const Scene *scene,
                                                 ViewLayer *view_layer)
{
  Object *ancestor = ob;
  while (ob->parent) {
    if (bc_is_in_Export_set(export_set, ob->parent, scene, view_layer)) {
      ancestor = ob->parent;
    }
    ob = ob->parent;
  }
  return ancestor;
}

void bc_get_children(std::vector<Object *> &child_set,
                     Object *ob,
                     const Scene *scene,
                     ViewLayer *view_layer)
{
  BKE_view_layer_synced_ensure(scene, view_layer);
  LISTBASE_FOREACH (Base *, base, BKE_view_layer_object_bases_get(view_layer)) {
    Object *cob = base->object;
    if (cob->parent == ob) {
      switch (ob->type) {
        case OB_MESH:
        case OB_CAMERA:
        case OB_LAMP:
        case OB_EMPTY:
        case OB_ARMATURE:
          child_set.push_back(cob);
        default:
          break;
      }
    }
  }
}

bool bc_is_in_Export_set(LinkNode *export_set,
                         Object *ob,
                         const Scene *scene,
                         ViewLayer *view_layer)
{
  bool to_export = (BLI_linklist_index(export_set, ob) != -1);

  if (!to_export) {
    /* Mark this object as to_export even if it is not in the
     * export list, but it contains children to export. */

    std::vector<Object *> children;
    bc_get_children(children, ob, scene, view_layer);
    for (Object *child : children) {
      if (bc_is_in_Export_set(export_set, child, scene, view_layer)) {
        to_export = true;
        break;
      }
    }
  }
  return to_export;
}

int bc_is_marked(Object *ob)
{
  return ob && (ob->id.tag & LIB_TAG_DOIT);
}

void bc_remove_mark(Object *ob)
{
  ob->id.tag &= ~LIB_TAG_DOIT;
}

void bc_set_mark(Object *ob)
{
  ob->id.tag |= LIB_TAG_DOIT;
}

IxamContext::IxamContext(bContext *C)
{
  context = C;
  main = CTX_data_main(C);
  scene = CTX_data_scene(C);
  view_layer = CTX_data_view_layer(C);
  depsgraph = nullptr; /* create only when needed */
}

bContext *IxamContext::get_context()
{
  return context;
}

Depsgraph *IxamContext::get_depsgraph()
{
  if (!depsgraph) {
    depsgraph = BKE_scene_ensure_depsgraph(main, scene, view_layer);
  }
  return depsgraph;
}

Scene *IxamContext::get_scene()
{
  return scene;
}

Scene *IxamContext::get_evaluated_scene()
{
  Scene *scene_eval = DEG_get_evaluated_scene(get_depsgraph());
  return scene_eval;
}

Object *IxamContext::get_evaluated_object(Object *ob)
{
  Object *ob_eval = DEG_get_evaluated_object(depsgraph, ob);
  return ob_eval;
}

ViewLayer *IxamContext::get_view_layer()
{
  return view_layer;
}

Main *IxamContext::get_main()
{
  return main;
}
