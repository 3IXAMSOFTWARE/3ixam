

/** \file
 * \ingroup spnode
 */

#include "DNA_gpencil_types.h"
#include "DNA_light_types.h"
#include "DNA_material_types.h"
#include "DNA_node_types.h"
#include "DNA_world_types.h"

#include "MEM_guardedalloc.h"

#include "BKE_context.h"
#include "BKE_gpencil.h"
#include "BKE_lib_id.h"
#include "BKE_lib_remap.h"
#include "BKE_node.h"
#include "BKE_screen.h"

#include "ED_matpro.h"
#include "ED_render.h"
#include "ED_screen.h"
#include "ED_space_api.h"

#include "UI_resources.h"
#include "UI_view2d.h"

#include "BLO_read_write.h"

#include "RNA_access.h"
#include "RNA_define.h"
#include "RNA_enum_types.h"
#include "RNA_prototypes.h"

#include "WM_api.h"
#include "WM_types.h"

#include "matpro_intern.hh" /* own include */

using ixam::float2;

/* ******************** tree path ********************* */

void ED_matpro_tree_start(SpaceMatPro *smatpro, bNodeTree *ntree, ID *id, ID *from)
{
  LISTBASE_FOREACH_MUTABLE (bNodeTreePath *, path, &smatpro->treepath) {
    MEM_freeN(path);
  }
  BLI_listbase_clear(&smatpro->treepath);

  if (ntree) {
    bNodeTreePath *path = MEM_cnew<bNodeTreePath>("node tree path");
    path->nodetree = ntree;
    path->parent_key = NODE_INSTANCE_KEY_BASE;

    /* copy initial offset from bNodeTree */
    copy_v2_v2(path->view_center, ntree->view_center);

    if (id) {
      BLI_strncpy(path->display_name, id->name + 2, sizeof(path->display_name));
    }

    BLI_addtail(&smatpro->treepath, path);

    if (ntree->type != NTREE_GEOMETRY) {
      /* This can probably be removed for all node tree types. It mainly exists because it was not
       * possible to store id references in custom properties. Also see T36024. I don't want to
       * remove it for all tree types in bcon3 though. */
      id_us_ensure_real(&ntree->id);
    }
  }

  /* update current tree */
  smatpro->nodetree = smatpro->edittree = ntree;
  smatpro->id = id;
  smatpro->from = from;

  ED_matpro_set_active_viewer_key(smatpro);

  WM_main_add_notifier(NC_SCENE | ND_NODES, nullptr);
}

void ED_matpro_tree_push(SpaceMatPro *smatpro, bNodeTree *ntree, bNode *gnode)
{
  bNodeTreePath *path = MEM_cnew<bNodeTreePath>("node tree path");
  bNodeTreePath *prev_path = (bNodeTreePath *)smatpro->treepath.last;
  path->nodetree = ntree;
  if (gnode) {
    if (prev_path) {
      path->parent_key = BKE_node_instance_key(prev_path->parent_key, prev_path->nodetree, gnode);
    }
    else {
      path->parent_key = NODE_INSTANCE_KEY_BASE;
    }

    BLI_strncpy(path->node_name, gnode->name, sizeof(path->node_name));
    BLI_strncpy(path->display_name, gnode->name, sizeof(path->display_name));
  }
  else {
    path->parent_key = NODE_INSTANCE_KEY_BASE;
  }

  /* copy initial offset from bNodeTree */
  copy_v2_v2(path->view_center, ntree->view_center);

  BLI_addtail(&smatpro->treepath, path);

  id_us_ensure_real(&ntree->id);

  /* update current tree */
  smatpro->edittree = ntree;

  ED_matpro_set_active_viewer_key(smatpro);

  WM_main_add_notifier(NC_SCENE | ND_NODES, nullptr);
}

void ED_matpro_tree_pop(SpaceMatPro *smatpro)
{
  bNodeTreePath *path = (bNodeTreePath *)smatpro->treepath.last;

  /* don't remove root */
  if (path == smatpro->treepath.first) {
    return;
  }

  BLI_remlink(&smatpro->treepath, path);
  MEM_freeN(path);

  /* update current tree */
  path = (bNodeTreePath *)smatpro->treepath.last;
  smatpro->edittree = path->nodetree;

  ED_matpro_set_active_viewer_key(smatpro);

  /* listener updates the View2D center from edittree */
  WM_main_add_notifier(NC_SCENE | ND_NODES, nullptr);
}

int ED_matpro_tree_depth(SpaceMatPro *smatpro)
{
  return BLI_listbase_count(&smatpro->treepath);
}

bNodeTree *ED_matpro_tree_get(SpaceMatPro *smatpro, int level)
{
  bNodeTreePath *path;
  int i;
  for (path = (bNodeTreePath *)smatpro->treepath.last, i = 0; path; path = path->prev, i++) {
    if (i == level) {
      return path->nodetree;
    }
  }
  return nullptr;
}

int ED_matpro_tree_path_length(SpaceMatPro *smatpro)
{
  int length = 0;
  int i = 0;
  LISTBASE_FOREACH_INDEX (bNodeTreePath *, path, &smatpro->treepath, i) {
    length += strlen(path->display_name);
    if (i > 0) {
      length += 1; /* for separator char */
    }
  }
  return length;
}

void ED_matpro_tree_path_get(SpaceMatPro *smatpro, char *value)
{
  int i = 0;

  value[0] = '\0';
  LISTBASE_FOREACH_INDEX (bNodeTreePath *, path, &smatpro->treepath, i) {
    if (i == 0) {
      strcpy(value, path->display_name);
      value += strlen(path->display_name);
    }
    else {
      BLI_sprintf(value, "/%s", path->display_name);
      value += strlen(path->display_name) + 1;
    }
  }
}

void ED_matpro_set_active_viewer_key(SpaceMatPro *smatpro)
{
  bNodeTreePath *path = (bNodeTreePath *)smatpro->treepath.last;
  if (smatpro->nodetree && path) {
    smatpro->nodetree->active_viewer_key = path->parent_key;
  }
}

void ED_matpro_cursor_location_get(const SpaceMatPro *smatpro, float value[2])
{
  copy_v2_v2(value, smatpro->runtime->cursor);
}

void ED_matpro_cursor_location_set(SpaceMatPro *smatpro, const float value[2])
{
  copy_v2_v2(smatpro->runtime->cursor, value);
}

namespace ixam::ed::space_matpro {

float2 space_matpro_group_offset(const SpaceMatPro &smatpro)
{
  const bNodeTreePath *path = (bNodeTreePath *)smatpro.treepath.last;

  if (path && path->prev) {
    return float2(path->view_center) - float2(path->prev->view_center);
  }
  return float2(0);
}

/* ******************** default callbacks for node space ***************** */

static SpaceLink *matpro_create(const ScrArea * /*area*/, const Scene * /*scene*/)
{
  SpaceMatPro *smatpro = MEM_cnew<SpaceMatPro>("initsmatpro");
  smatpro->spacetype = SPACE_MATPRO;

  smatpro->flag = SNODE_SHOW_GPENCIL | SNODE_USE_ALPHA;
  smatpro->overlay.flag = (SN_OVERLAY_SHOW_OVERLAYS | SN_OVERLAY_SHOW_WIRE_COLORS |
                         SN_OVERLAY_SHOW_PATH);

  /* backdrop */
  smatpro->zoom = 1.0f;

  /* select the first tree type for valid type */
  NODE_TREE_TYPES_BEGIN (treetype) {
    if (strcmp(treetype->idname, "ShaderNodeTree") == 0) {
      strcpy(smatpro->tree_idname, treetype->idname);
      break;
    }
  }
  NODE_TREE_TYPES_END;

  /* header */
  ARegion *region = MEM_cnew<ARegion>("header for matpro");

  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_HEADER;
  region->alignment = RGN_ALIGN_TOP;
  region->overlap = false;

  /* preview */
  region = MEM_cnew<ARegion>("preview for matpro");
  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_PREVIEW;
  region->alignment = RGN_ALIGN_RIGHT;

  /* props */
  region = MEM_cnew<ARegion>("props for matpro");
  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_EXECUTE;
  region->alignment = RGN_ALIGN_BOTTOM | RGN_SPLIT_PREV;

  /* materials */
  region = MEM_cnew<ARegion>("materials for matpro");

  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_UI;
  region->alignment = RGN_ALIGN_TOP;
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.minzoom = region->v2d.maxzoom = 1.0f;
  region->v2d.flag = V2D_VIEWSYNC_AREA_VERTICAL;
  region->overlap = false;

  /* materials */
  region = MEM_cnew<ARegion>("navbar for matpro");

  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_NAV_BAR;
  region->alignment = RGN_ALIGN_LEFT;
  region->overlap = false;
  region->v2d.scroll = V2D_SCROLL_VERTICAL_HIDE;

  /* toolbar */
  region = MEM_cnew<ARegion>("palette matpro");

  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_TOOLS;
  region->alignment = RGN_ALIGN_LEFT;
  region->overlap = false;

  /* tabs */
  region = MEM_cnew<ARegion>("tabs matpro");

  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_TOOL_HEADER;
  region->alignment = RGN_ALIGN_TOP;
  region->overlap = false;

  /* main region */
  region = MEM_cnew<ARegion>("main region for matpro");
  BLI_addtail(&smatpro->regionbase, region);
  region->regiontype = RGN_TYPE_WINDOW;

  region->v2d.tot.xmin = -12.8f * U.widget_unit;
  region->v2d.tot.ymin = -12.8f * U.widget_unit;
  region->v2d.tot.xmax = 38.4f * U.widget_unit;
  region->v2d.tot.ymax = 38.4f * U.widget_unit;

  region->v2d.cur = region->v2d.tot;

  region->v2d.min[0] = 1.0f;
  region->v2d.min[1] = 1.0f;

  region->v2d.max[0] = 32000.0f;
  region->v2d.max[1] = 32000.0f;

  region->v2d.minzoom = 0.05f;
  region->v2d.maxzoom = 2.31f;

  region->v2d.scroll = (V2D_SCROLL_RIGHT | V2D_SCROLL_BOTTOM);
  region->v2d.keepzoom = V2D_LIMITZOOM | V2D_KEEPASPECT;
  region->v2d.keeptot = 0;

  return (SpaceLink *)smatpro;
}

static void matpro_free(SpaceLink *sl)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)sl;

  LISTBASE_FOREACH_MUTABLE (bNodeTreePath *, path, &smatpro->treepath) {
    MEM_freeN(path);
  }

  if (smatpro->runtime) {
    smatpro->runtime->linkdrag.reset();
    MEM_delete(smatpro->runtime);
  }
}

/* spacetype; init callback */
static void matpro_init(wmWindowManager * /*wm*/, ScrArea *area)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)area->spacedata.first;

  if (smatpro->runtime == nullptr) {
    smatpro->runtime = MEM_new<SpaceMatPro_Runtime>(__func__);
  }
}

static bool any_node_uses_id(const bNodeTree *ntree, const ID *id)
{
  if (ELEM(nullptr, ntree, id)) {
    return false;
  }
  LISTBASE_FOREACH (bNode *, node, &ntree->nodes) {
    if (node->id == id) {
      return true;
    }
  }
  return false;
}

/**
 * Tag the space to recalculate the compositing tree using auto-compositing pipeline.
 *
 * Will check the space to be using a compositing tree, and check whether auto-compositing
 * is enabled. If the checks do not pass then the function has no affect.
 */
static void node_area_tag_recalc_auto_compositing(SpaceMatPro *smatpro, ScrArea *area)
{
  if (!ED_matpro_is_compositor(smatpro)) {
    return;
  }

  if (smatpro->flag & SNODE_AUTO_RENDER) {
    smatpro->runtime->recalc_auto_compositing = true;
    ED_area_tag_refresh(area);
  }
}

/**
 * Tag the space to recalculate the current tree.
 *
 * For all node trees this will do `smatpro_set_context()` which takes care of setting an active
 * tree. This will be done in the area refresh callback.
 *
 * For compositor tree this will additionally start of the compositor job.
 */
static void node_area_tag_tree_recalc(SpaceMatPro *smatpro, ScrArea *area)
{
  if (ED_matpro_is_compositor(smatpro)) {
    smatpro->runtime->recalc_regular_compositing = true;
  }

  ED_area_tag_refresh(area);
}

static void matpro_area_listener(const wmSpaceTypeListenerParams *params)
{
  ScrArea *area = params->area;
  const wmNotifier *wmn = params->notifier;

  /* NOTE: #ED_area_tag_refresh will re-execute compositor. */
  SpaceMatPro *smatpro = (SpaceMatPro *)area->spacedata.first;
  /* shaderfrom is only used for new shading nodes, otherwise all shaders are from objects */
  short shader_type = smatpro->shaderfrom;

  /* preview renders */
  switch (wmn->category) {
    case NC_SCENE:
      switch (wmn->data) {
        case ND_NODES: {
          ARegion *region = BKE_area_find_region_type(area, RGN_TYPE_WINDOW);
          bNodeTreePath *path = (bNodeTreePath *)smatpro->treepath.last;
          /* shift view to node tree center */
          if (region && path) {
            UI_view2d_center_set(&region->v2d, path->view_center[0], path->view_center[1]);
          }

          node_area_tag_tree_recalc(smatpro, area);
          break;
        }
        case ND_FRAME:
          node_area_tag_tree_recalc(smatpro, area);
          break;
        case ND_COMPO_RESULT:
          ED_area_tag_redraw(area);
          break;
        case ND_TRANSFORM_DONE:
          node_area_tag_recalc_auto_compositing(smatpro, area);
          break;
        case ND_LAYER_CONTENT:
          node_area_tag_tree_recalc(smatpro, area);
          break;
      }
      break;

    /* future: add ID checks? */
    case NC_MATERIAL: {
      ScrArea *area = params->area;
      ED_area_tag_redraw(area);
      switch (wmn->data) {
        case ND_SHADING:
        case ND_SHADING_DRAW:
        case ND_SHADING_LINKS:
        case ND_SHADING_PREVIEW:
        // case ND_NODES:
          smatpro->preview = 1;
          break;
      }

      if (ED_matpro_is_shader(smatpro)) {
        if (ELEM(wmn->data, ND_SHADING, ND_SHADING_DRAW, ND_SHADING_LINKS)) {
          node_area_tag_tree_recalc(smatpro, area);
        }
      }
    } break;
    case NC_TEXTURE:
      if (ED_matpro_is_shader(smatpro) || ED_matpro_is_texture(smatpro)) {
        if (wmn->data == ND_NODES) {
          node_area_tag_tree_recalc(smatpro, area);
        }
      }
      break;
    case NC_WORLD:
      if (ED_matpro_is_shader(smatpro) && shader_type == SNODE_SHADER_WORLD) {
        node_area_tag_tree_recalc(smatpro, area);
      }
      break;
    case NC_OBJECT:
      if (ED_matpro_is_shader(smatpro)) {
        if (wmn->data == ND_OB_SHADING) {
          node_area_tag_tree_recalc(smatpro, area);
        }
      }
      else if (ED_matpro_is_geometry(smatpro)) {
        /* Rather strict check: only redraw when the reference matches the current editor's ID. */
        if (wmn->data == ND_MODIFIER) {
          if (wmn->reference == smatpro->id || smatpro->id == nullptr) {
            node_area_tag_tree_recalc(smatpro, area);
          }
        }
      }
      break;
    case NC_SPACE:
      if (wmn->data == ND_SPACE_MATPRO) {
        node_area_tag_tree_recalc(smatpro, area);
      }
      else if (wmn->data == ND_SPACE_MATPRO_VIEW) {
        ED_area_tag_redraw(area);
      }
      break;
    case NC_NODE:
      if (wmn->action == NA_EDITED) {
        node_area_tag_tree_recalc(smatpro, area);
      }
      else if (wmn->action == NA_SELECTED) {
        ED_area_tag_redraw(area);
      }
      break;
    case NC_SCREEN:
      switch (wmn->data) {
        case ND_ANIMPLAY:
          node_area_tag_tree_recalc(smatpro, area);
          break;
      }
      break;
    case NC_MASK:
      if (wmn->action == NA_EDITED) {
        if (smatpro->nodetree && smatpro->nodetree->type == NTREE_COMPOSIT) {
          node_area_tag_tree_recalc(smatpro, area);
        }
      }
      break;

    case NC_IMAGE:
      if (wmn->action == NA_EDITED) {
        if (ED_matpro_is_compositor(smatpro)) {
          /* Without this check drawing on an image could become very slow when the compositor is
           * open. */
          if (any_node_uses_id(smatpro->nodetree, (ID *)wmn->reference)) {
            node_area_tag_tree_recalc(smatpro, area);
          }
        }
      }
      break;

    case NC_MOVIECLIP:
      if (wmn->action == NA_EDITED) {
        if (ED_matpro_is_compositor(smatpro)) {
          if (any_node_uses_id(smatpro->nodetree, (ID *)wmn->reference)) {
            node_area_tag_tree_recalc(smatpro, area);
          }
        }
      }
      break;

    case NC_LINESTYLE:
      if (ED_matpro_is_shader(smatpro) && shader_type == SNODE_SHADER_LINESTYLE) {
        node_area_tag_tree_recalc(smatpro, area);
      }
      break;
    case NC_WM:
      if (wmn->data == ND_UNDO) {
        node_area_tag_tree_recalc(smatpro, area);
      }
      break;
    case NC_GPENCIL:
      if (ELEM(wmn->action, NA_EDITED, NA_SELECTED)) {
        ED_area_tag_redraw(area);
      }
      break;
  }
}

static void matpro_area_refresh(const bContext *C, ScrArea *area)
{
  /* default now: refresh node is starting preview */
  SpaceMatPro *smatpro = (SpaceMatPro *)area->spacedata.first;

  smatpro_set_context(*C);

  if (smatpro->nodetree) {
    if (smatpro->nodetree->type == NTREE_COMPOSIT) {
      Scene *scene = (Scene *)smatpro->id;
      if (scene->use_nodes) {
        /* recalc is set on 3d view changes for auto compo */
        if (smatpro->runtime->recalc_auto_compositing) {
          smatpro->runtime->recalc_auto_compositing = false;
          smatpro->runtime->recalc_regular_compositing = false;
          node_render_changed_exec((bContext *)C, nullptr);
        }
        else if (smatpro->runtime->recalc_regular_compositing) {
          smatpro->runtime->recalc_regular_compositing = false;
          ED_matpro_composite_job(C, smatpro->nodetree, scene);
        }
      }
    }
  }
}

static SpaceLink *matpro_duplicate(SpaceLink *sl)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)sl;
  SpaceMatPro *smatpron = (SpaceMatPro *)MEM_dupallocN(smatpro);

  BLI_duplicatelist(&smatpron->treepath, &smatpro->treepath);

  smatpron->runtime = nullptr;

  /* NOTE: no need to set node tree user counts,
   * the editor only keeps at least 1 (id_us_ensure_real),
   * which is already done by the original SpaceMatPro.
   */

  return (SpaceLink *)smatpron;
}

/* add handlers, stuff you only do once or on area/region changes */
static void matpro_buttons_region_init(wmWindowManager *wm, ARegion *region)
{
  wmKeyMap *keymap;

  ED_region_panels_init(wm, region);

  keymap = WM_keymap_ensure(wm->defaultconf, "Node Generic", SPACE_NODE, 0);
  WM_event_add_keymap_handler(&region->handlers, keymap);
}

static void matpro_buttons_region_draw(const bContext *C, ARegion *region)
{
  ED_region_panels(C, region);
}

/* add handlers, stuff you only do once or on area/region changes */
static void matpro_ui_region_init(wmWindowManager *wm, ARegion *region)
{
  wmKeyMap *keymap;

  UI_view2d_region_reinit(&region->v2d, V2D_COMMONVIEW_PANELS_UI, region->winx, region->winy);
  region->v2d.keepzoom |= V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y;
  keymap = WM_keymap_ensure(wm->defaultconf, "View2D Buttons List", 0, 0);
  WM_event_add_keymap_handler(&region->handlers, keymap);

  // keymap = WM_keymap_ensure(wm->defaultconf, "MatPro Material List", SPACE_MATPRO, 0);
  // WM_event_add_keymap_handler(&region->handlers, keymap);
}

/* add handlers, stuff you only do once or on area/region changes */
static void matpro_toolbar_region_init(wmWindowManager *wm, ARegion *region)
{
  wmKeyMap *keymap;

  ED_region_panels_init(wm, region);

  region->v2d.keepzoom |= V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y;

  keymap = WM_keymap_ensure(wm->defaultconf, "Node Generic", SPACE_NODE, 0);
  WM_event_add_keymap_handler(&region->handlers, keymap);
}

static void matpro_toolbar_region_draw(const bContext *C, ARegion *region)
{
  ED_region_panels(C, region);
}

static void matpro_toolbar_region_layout(const bContext *C, ARegion *region)
{
  SpaceMatPro *smatpro = CTX_wm_space_matpro(C);
  char id_lower[64];
  const char *contexts[2] = {id_lower, NULL};

  /* Avoid duplicating identifiers, use existing RNA enum. */
  {
    const EnumPropertyItem *items = rna_enum_palette_section_items;
    int i = RNA_enum_from_value(items, smatpro->palette_section_active);
    /* File is from the future. */
    if (i == -1) {
      i = 0;
    }
    const char *id = items[i].identifier;
    BLI_assert(strlen(id) < sizeof(id_lower));
    STRNCPY(id_lower, id);
    BLI_str_tolower_ascii(id_lower, strlen(id_lower));
  }

  ED_region_panels_layout_ex(C, region, &region->type->paneltypes, contexts, NULL);
}

static void matpro_preview_region_init(wmWindowManager *wm, ARegion *region)
{
  ED_region_panels_init(wm, region);
  region->v2d.keepzoom |= V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y;
}

static void matpro_preview_region_draw(const bContext *C, ARegion *region)
{
  ED_region_panels(C, region);
}

static void matpro_cursor(wmWindow *win, ScrArea *area, ARegion *region)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)area->spacedata.first;

  /* convert mouse coordinates to v2d space */
  UI_view2d_region_to_view(&region->v2d,
                           win->eventstate->xy[0] - region->winrct.xmin,
                           win->eventstate->xy[1] - region->winrct.ymin,
                           &smatpro->runtime->cursor[0],
                           &smatpro->runtime->cursor[1]);

  /* here smatpro->runtime->cursor is used to detect the node edge for sizing */
  node_set_cursor(*win, *smatpro, smatpro->runtime->cursor);

  /* XXX smatpro->runtime->cursor is in placing new nodes space */
  smatpro->runtime->cursor[0] /= UI_DPI_FAC;
  smatpro->runtime->cursor[1] /= UI_DPI_FAC;
}

/* Initialize main region, setting handlers. */
static void matpro_main_region_init(wmWindowManager *wm, ARegion *region)
{
  wmKeyMap *keymap;
  ListBase *lb;

  UI_view2d_region_reinit(&region->v2d, V2D_COMMONVIEW_CUSTOM, region->winx, region->winy);
  region->v2d.scroll |= (V2D_SCROLL_VERTICAL_HIDE | V2D_SCROLL_HORIZONTAL_HIDE);

  /* own keymaps */
  keymap = WM_keymap_ensure(wm->defaultconf, "MatPro Generic", SPACE_MATPRO, 0);
  WM_event_add_keymap_handler(&region->handlers, keymap);

  keymap = WM_keymap_ensure(wm->defaultconf, "MatPro Editor", SPACE_MATPRO, 0);
  WM_event_add_keymap_handler_v2d_mask(&region->handlers, keymap);

  /* add drop boxes */
  lb = WM_dropboxmap_find("MatPro Editor", SPACE_MATPRO, RGN_TYPE_WINDOW);

  WM_event_add_dropbox_handler(&region->handlers, lb);

  /* The backdrop image gizmo needs to change together with the view. So always refresh gizmos on
   * region size changes. */
  WM_gizmomap_tag_refresh(region->gizmo_map);
}

static void matpro_main_region_draw(const bContext *C, ARegion *region)
{
  node_draw_space(*C, *region);
}

/* ************* dropboxes ************* */

static bool node_group_drop_poll(bContext * /*C*/, wmDrag *drag, const wmEvent * /*event*/)
{
  return WM_drag_is_ID_type(drag, ID_NT);
}

static bool node_object_drop_poll(bContext * /*C*/, wmDrag *drag, const wmEvent * /*event*/)
{
  return WM_drag_is_ID_type(drag, ID_OB);
}

static bool node_collection_drop_poll(bContext * /*C*/, wmDrag *drag, const wmEvent * /*event*/)
{
  return WM_drag_is_ID_type(drag, ID_GR);
}

static bool node_ima_drop_poll(bContext * /*C*/, wmDrag *drag, const wmEvent * /*event*/)
{
  if (drag->type == WM_DRAG_PATH) {
    /* rule might not work? */
    return ELEM(drag->icon, 0, ICON_FILE_IMAGE, ICON_FILE_MOVIE);
  }
  return WM_drag_is_ID_type(drag, ID_IM);
}

static bool node_mask_drop_poll(bContext * /*C*/, wmDrag *drag, const wmEvent * /*event*/)
{
  return WM_drag_is_ID_type(drag, ID_MSK);
}

static void node_group_drop_copy(bContext * /*C*/, wmDrag *drag, wmDropBox *drop)
{
  ID *id = WM_drag_get_local_ID_or_import_from_asset(drag, 0);

  RNA_int_set(drop->ptr, "session_uuid", int(id->session_uuid));
}

static void node_id_drop_copy(bContext * /*C*/, wmDrag *drag, wmDropBox *drop)
{
  ID *id = WM_drag_get_local_ID_or_import_from_asset(drag, 0);

  RNA_int_set(drop->ptr, "session_uuid", int(id->session_uuid));
}

static void node_id_path_drop_copy(bContext * /*C*/, wmDrag *drag, wmDropBox *drop)
{
  ID *id = WM_drag_get_local_ID_or_import_from_asset(drag, 0);

  if (id) {
    RNA_int_set(drop->ptr, "session_uuid", int(id->session_uuid));
    RNA_struct_property_unset(drop->ptr, "filepath");
  }
  else if (drag->path[0]) {
    RNA_string_set(drop->ptr, "filepath", drag->path);
    RNA_struct_property_unset(drop->ptr, "name");
  }
}

/* this region dropbox definition */
static void matpro_dropboxes()
{
  ListBase *lb = WM_dropboxmap_find("MatPro Editor", SPACE_MATPRO, RGN_TYPE_WINDOW);

  WM_dropbox_add(lb,
                 "MATPRO_OT_add_object",
                 node_object_drop_poll,
                 node_id_drop_copy,
                 WM_drag_free_imported_drag_ID,
                 nullptr);
  WM_dropbox_add(lb,
                 "MATPRO_OT_add_collection",
                 node_collection_drop_poll,
                 node_id_drop_copy,
                 WM_drag_free_imported_drag_ID,
                 nullptr);
  WM_dropbox_add(lb,
                 "MATPRO_OT_add_group",
                 node_group_drop_poll,
                 node_group_drop_copy,
                 WM_drag_free_imported_drag_ID,
                 nullptr);
  WM_dropbox_add(lb,
                 "MATPRO_OT_add_file",
                 node_ima_drop_poll,
                 node_id_path_drop_copy,
                 WM_drag_free_imported_drag_ID,
                 nullptr);
  WM_dropbox_add(lb,
                 "MATPRO_OT_add_mask",
                 node_mask_drop_poll,
                 node_id_drop_copy,
                 WM_drag_free_imported_drag_ID,
                 nullptr);
}

/* ************* end drop *********** */

/* add handlers, stuff you only do once or on area/region changes */
static void matpro_header_region_init(wmWindowManager * /*wm*/, ARegion *region)
{
  ED_region_header_init(region);
}

static void matpro_header_region_draw(const bContext *C, ARegion *region)
{
  /* find and set the context */
  smatpro_set_context(*C);

  ED_region_header(C, region);
}

/* used for header + main region */
static void matpro_region_listener(const wmRegionListenerParams *params)
{
  ARegion *region = params->region;
  const wmNotifier *wmn = params->notifier;
  wmGizmoMap *gzmap = region->gizmo_map;

  /* context changes */
  switch (wmn->category) {
    case NC_SPACE:
      switch (wmn->data) {
        case ND_SPACE_NODE:
          ED_region_tag_redraw(region);
          break;
        case ND_SPACE_NODE_VIEW:
          WM_gizmomap_tag_refresh(gzmap);
          break;
      }
      break;
    case NC_SCREEN:
      if (wmn->data == ND_LAYOUTSET || wmn->action == NA_EDITED) {
        WM_gizmomap_tag_refresh(gzmap);
      }
      switch (wmn->data) {
        case ND_ANIMPLAY:
        case ND_LAYER:
          ED_region_tag_redraw(region);
          break;
      }
      break;
    case NC_WM:
      if (wmn->data == ND_JOB) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_SCENE:
      ED_region_tag_redraw(region);
      if (wmn->data == ND_RENDER_RESULT) {
        WM_gizmomap_tag_refresh(gzmap);
      }
      break;
    case NC_NODE:
      ED_region_tag_redraw(region);
      if (ELEM(wmn->action, NA_EDITED, NA_SELECTED)) {
        WM_gizmomap_tag_refresh(gzmap);
      }
      break;
    case NC_MATERIAL:
    case NC_TEXTURE:
    case NC_WORLD:
    case NC_LINESTYLE:
      ED_region_tag_redraw(region);
      break;
    case NC_OBJECT:
      if (wmn->data == ND_OB_SHADING) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_ID:
      if (wmn->action == NA_RENAME) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_GPENCIL:
      if (wmn->action == NA_EDITED) {
        ED_region_tag_redraw(region);
      }
      else if (wmn->data & ND_GPENCIL_EDITMODE) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_VIEWER_PATH:
      ED_region_tag_redraw(region);
      break;
  }
}

static void matpro_navigation_region_listener(const wmRegionListenerParams *UNUSED(params))
{
}

}  // namespace ixam::ed::space_matpro

/* Outside of ixam namespace to avoid Python documentation build error with `ctypes`. */
extern "C" {
const char *matpro_context_dir[] = {
    "selected_nodes", "active_node", "light", "material", "world", nullptr};
};

namespace ixam::ed::space_matpro {

static int /*eContextResult*/ matpro_context(const bContext *C,
                                           const char *member,
                                           bContextDataResult *result)
{
  SpaceMatPro *smatpro = CTX_wm_space_matpro(C);

  if (CTX_data_dir(member)) {
    CTX_data_dir_set(result, matpro_context_dir);
    return CTX_RESULT_OK;
  }
  if (CTX_data_equals(member, "selected_nodes")) {
    if (smatpro->edittree) {
      LISTBASE_FOREACH_BACKWARD (bNode *, node, &smatpro->edittree->nodes) {
        if (node->flag & NODE_SELECT) {
          CTX_data_list_add(result, &smatpro->edittree->id, &RNA_Node, node);
        }
      }
    }
    CTX_data_type_set(result, CTX_DATA_TYPE_COLLECTION);
    return CTX_RESULT_OK;
  }
  if (CTX_data_equals(member, "active_node")) {
    if (smatpro->edittree) {
      bNode *node = nodeGetActive(smatpro->edittree);
      CTX_data_pointer_set(result, &smatpro->edittree->id, &RNA_Node, node);
    }

    CTX_data_type_set(result, CTX_DATA_TYPE_POINTER);
    return CTX_RESULT_OK;
  }
  if (CTX_data_equals(member, "node_previews")) {
    if (smatpro->nodetree) {
      CTX_data_pointer_set(
          result, &smatpro->nodetree->id, &RNA_NodeInstanceHash, smatpro->nodetree->previews);
    }

    CTX_data_type_set(result, CTX_DATA_TYPE_POINTER);
    return CTX_RESULT_OK;
  }
  if (CTX_data_equals(member, "material")) {
    if (smatpro->id && GS(smatpro->id->name) == ID_MA) {
      CTX_data_id_pointer_set(result, smatpro->id);
    }
    return CTX_RESULT_OK;
  }
  if (CTX_data_equals(member, "light")) {
    if (smatpro->id && GS(smatpro->id->name) == ID_LA) {
      CTX_data_id_pointer_set(result, smatpro->id);
    }
    return CTX_RESULT_OK;
  }
  if (CTX_data_equals(member, "world")) {
    if (smatpro->id && GS(smatpro->id->name) == ID_WO) {
      CTX_data_id_pointer_set(result, smatpro->id);
    }
    return CTX_RESULT_OK;
  }

  return CTX_RESULT_MEMBER_NOT_FOUND;
}

static void matpro_widgets()
{
//  /* Create the widget-map for the area here. */
//  wmGizmoMapType_Params params{SPACE_NODE, RGN_TYPE_WINDOW};
//  wmGizmoMapType *gzmap_type = WM_gizmomaptype_ensure(&params);
//  WM_gizmogrouptype_append_and_link(gzmap_type, NODE_GGT_backdrop_transform);
//  WM_gizmogrouptype_append_and_link(gzmap_type, NODE_GGT_backdrop_crop);
//  WM_gizmogrouptype_append_and_link(gzmap_type, NODE_GGT_backdrop_sun_beams);
//  WM_gizmogrouptype_append_and_link(gzmap_type, NODE_GGT_backdrop_corner_pin);
}

static void matpro_id_remap_cb(ID *old_id, ID *new_id, void *user_data)
{
  SpaceMatPro *smatpro = static_cast<SpaceMatPro *>(user_data);

  if (smatpro->id == old_id) {
    /* nasty DNA logic for SpaceMatPro:
     * ideally should be handled by editor code, but would be bad level call
     */
    BLI_freelistN(&smatpro->treepath);

    /* XXX Untested in case new_id != nullptr... */
    smatpro->id = new_id;
    smatpro->from = nullptr;
    smatpro->nodetree = nullptr;
    smatpro->edittree = nullptr;
  }
  else if (GS(old_id->name) == ID_OB) {
    if (smatpro->from == old_id) {
      if (new_id == nullptr) {
        smatpro->flag &= ~SNODE_PIN;
      }
      smatpro->from = new_id;
    }
  }
  else if (GS(old_id->name) == ID_GD) {
    if ((ID *)smatpro->gpd == old_id) {
      smatpro->gpd = (bGPdata *)new_id;
      id_us_min(old_id);
      id_us_plus(new_id);
    }
  }
  else if (GS(old_id->name) == ID_NT) {
    bNodeTreePath *path, *path_next;

    for (path = (bNodeTreePath *)smatpro->treepath.first; path; path = path->next) {
      if ((ID *)path->nodetree == old_id) {
        path->nodetree = (bNodeTree *)new_id;
        id_us_ensure_real(new_id);
      }
      if (path == smatpro->treepath.first) {
        /* first nodetree in path is same as smatpro->nodetree */
        smatpro->nodetree = path->nodetree;
      }
      if (path->nodetree == nullptr) {
        break;
      }
    }

    /* remaining path entries are invalid, remove */
    for (; path; path = path_next) {
      path_next = path->next;

      BLI_remlink(&smatpro->treepath, path);
      MEM_freeN(path);
    }

    /* edittree is just the last in the path,
     * set this directly since the path may have been shortened above */
    if (smatpro->treepath.last) {
      path = (bNodeTreePath *)smatpro->treepath.last;
      smatpro->edittree = path->nodetree;
    }
    else {
      smatpro->edittree = nullptr;
    }
  }
}

static void matpro_id_remap(ScrArea * /*area*/, SpaceLink *slink, const IDRemapper *mappings)
{
  /* Although we should be able to perform all the mappings in a single go this lead to issues when
   * running the python test cases. Somehow the nodetree/edittree weren't updated to the new
   * pointers that generated a SEGFAULT.
   *
   * To move forward we should perhaps remove smatpro->edittree and smatpro->nodetree as they are just
   * copies of pointers. All usages should be calling a function that will receive the appropriate
   * instance.
   *
   * We could also move a remap address at a time to use the IDRemapper as that should get closer
   * to cleaner code. See {D13615} for more information about this topic.
   */
  BKE_id_remapper_iter(mappings, matpro_id_remap_cb, slink);

}

static int matpro_space_subtype_get(ScrArea *area)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)area->spacedata.first;
  return rna_node_tree_idname_to_enum(smatpro->tree_idname);
}

static void matpro_space_subtype_set(ScrArea *area, int value)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)area->spacedata.first;
  ED_matpro_set_tree_type(smatpro, rna_node_tree_type_from_enum(value));
}

static void matpro_space_subtype_item_extend(bContext *C, EnumPropertyItem **item, int *totitem)
{
  bool free;
  const EnumPropertyItem *item_src = RNA_enum_node_tree_types_itemf_impl(C, &free);
  RNA_enum_items_add(item, totitem, item_src);
  if (free) {
    MEM_freeN((void *)item_src);
  }
}

static void matpro_ixam_read_data(IxamDataReader *reader, SpaceLink *sl)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)sl;

  if (smatpro->gpd) {
    BLO_read_data_address(reader, &smatpro->gpd);
    BKE_gpencil_ixam_read_data(reader, smatpro->gpd);
  }

  BLO_read_list(reader, &smatpro->treepath);
  smatpro->edittree = nullptr;
  smatpro->runtime = nullptr;
}

static void matpro_ixam_read_lib(IxamLibReader *reader, ID *parent_id, SpaceLink *sl)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)sl;

  /* node tree can be stored locally in id too, link this first */
  BLO_read_id_address(reader, parent_id->lib, &smatpro->id);
  BLO_read_id_address(reader, parent_id->lib, &smatpro->from);

  bNodeTree *ntree = smatpro->id ? ntreeFromID(smatpro->id) : nullptr;
  if (ntree) {
    smatpro->nodetree = ntree;
  }
  else {
    BLO_read_id_address(reader, parent_id->lib, &smatpro->nodetree);
  }

  bNodeTreePath *path;
  for (path = static_cast<bNodeTreePath *>(smatpro->treepath.first); path; path = path->next) {
    if (path == smatpro->treepath.first) {
      /* first nodetree in path is same as smatpro->nodetree */
      path->nodetree = smatpro->nodetree;
    }
    else {
      BLO_read_id_address(reader, parent_id->lib, &path->nodetree);
    }

    if (!path->nodetree) {
      break;
    }
  }

  /* remaining path entries are invalid, remove */
  bNodeTreePath *path_next;
  for (; path; path = path_next) {
    path_next = path->next;

    BLI_remlink(&smatpro->treepath, path);
    MEM_freeN(path);
  }

  /* edittree is just the last in the path,
   * set this directly since the path may have been shortened above */
  if (smatpro->treepath.last) {
    path = static_cast<bNodeTreePath *>(smatpro->treepath.last);
    smatpro->edittree = path->nodetree;
  }
  else {
    smatpro->edittree = nullptr;
  }
}

static void matpro_ixam_write(IxamWriter *writer, SpaceLink *sl)
{
  SpaceMatPro *smatpro = (SpaceMatPro *)sl;
  BLO_write_struct(writer, SpaceMatPro, smatpro);

  LISTBASE_FOREACH (bNodeTreePath *, path, &smatpro->treepath) {
    BLO_write_struct(writer, bNodeTreePath, path);
  }
}

}  // namespace ixam::ed::space_matpro

void ED_spacetype_matpro()
{
  using namespace ixam::ed::space_matpro;

  SpaceType *st = MEM_cnew<SpaceType>("spacetype matpro");
  ARegionType *art;

  st->spaceid = SPACE_MATPRO;
  STRNCPY(st->name, "MatPro");

  st->create = matpro_create;
  st->free = matpro_free;
  st->init = matpro_init;
  st->duplicate = matpro_duplicate;
  st->operatortypes = matpro_operatortypes;
  st->keymap = matpro_keymap;
  st->listener = matpro_area_listener;
  st->refresh = matpro_area_refresh;
  st->context = matpro_context;
  st->dropboxes = matpro_dropboxes;
  st->gizmos = matpro_widgets;
  st->id_remap = matpro_id_remap;
  // st->space_subtype_item_extend = matpro_space_subtype_item_extend;
  // st->space_subtype_get = matpro_space_subtype_get;
  // st->space_subtype_set = matpro_space_subtype_set;
  st->ixam_read_data = matpro_ixam_read_data;
  st->ixam_read_lib = matpro_ixam_read_lib;
  st->ixam_write = matpro_ixam_write;

  /* regions: main window */
  art = MEM_cnew<ARegionType>("spacetype node region");
  art->regionid = RGN_TYPE_WINDOW;
  art->prefsizex = 1400;
  art->init = matpro_main_region_init;
  art->draw = matpro_main_region_draw;
  art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_GIZMO | ED_KEYMAP_TOOL | ED_KEYMAP_VIEW2D |
                    ED_KEYMAP_FRAMES | ED_KEYMAP_GPENCIL;
  art->listener = matpro_region_listener;
  art->cursor = matpro_cursor;
  art->event_cursor = true;
  art->clip_gizmo_events_by_ui = true;

  BLI_addhead(&st->regiontypes, art);

  /* regions: header */
  art = MEM_cnew<ARegionType>("spacetype node region");
  art->regionid = RGN_TYPE_HEADER;
  art->prefsizey = HEADERY;
  art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_VIEW2D | ED_KEYMAP_FRAMES | ED_KEYMAP_HEADER;
  art->listener = matpro_region_listener;
  art->init = matpro_header_region_init;
  art->draw = matpro_header_region_draw;

  BLI_addhead(&st->regiontypes, art);

  /* regions: listview/buttons */
  art = MEM_cnew<ARegionType>("spacetype material list region");
  art->regionid = RGN_TYPE_UI;
  art->prefsizey = 200;
   art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_FRAMES;
  // art->listener = matpro_region_listener;
  // art->message_subscribe = ED_area_do_mgs_subscribe_for_tool_ui;
  art->init = matpro_ui_region_init;
  art->draw = matpro_buttons_region_draw;
  art->keymapflag = ED_KEYMAP_UI;
  BLI_addhead(&st->regiontypes, art);

  /* regions: toolbar */
  art = MEM_cnew<ARegionType>("spacetype matpro palette region");
  art->regionid = RGN_TYPE_TOOLS;
  art->prefsizex = 200; /* XXX */
  // art->prefsizey = 50; /* XXX */
  art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_FRAMES;
  art->listener = matpro_region_listener;
  art->message_subscribe = ED_region_generic_tools_region_message_subscribe;
  art->snap_size = ED_region_generic_tools_region_snap_size;
  art->init = matpro_toolbar_region_init;
  art->draw = ED_region_panels_draw;
  art->layout = matpro_toolbar_region_layout;
  BLI_addhead(&st->regiontypes, art);

  /* regions: navbar */
  art = MEM_cnew<ARegionType>("spacetype matpro navbar region");
  art->regionid = RGN_TYPE_NAV_BAR;
  art->prefsizex = UI_NAVIGATION_REGION_WIDTH;
  art->init = matpro_toolbar_region_init;
  art->draw = matpro_toolbar_region_draw;
  art->listener = matpro_navigation_region_listener;
  art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_NAVBAR;
  BLI_addhead(&st->regiontypes, art);

  /* regions: preview */
  art = MEM_cnew<ARegionType>("spacetype matpro preview region");
  art->regionid = RGN_TYPE_PREVIEW;
  art->prefsizex = 260; /* XXX */
  // art->prefsizey = 270; /* XXX */
  art->listener = matpro_region_listener;
  art->init = matpro_preview_region_init;
  art->draw = matpro_preview_region_draw;
  art->keymapflag = ED_KEYMAP_UI;
  BLI_addhead(&st->regiontypes, art);

  /* regions: props */
  art = MEM_cnew<ARegionType>("spacetype matpro props region");
  art->regionid = RGN_TYPE_EXECUTE;
  art->prefsizey = 500; /* XXX */
  art->listener = matpro_region_listener;
  art->init = matpro_preview_region_init; // create new one if needed //
  art->draw = matpro_preview_region_draw; //                          //
  art->keymapflag = ED_KEYMAP_UI;
  BLI_addhead(&st->regiontypes, art);

  /* regions: tabs */
  art = MEM_cnew<ARegionType>("spacetype matpro tabs region");
  art->regionid = RGN_TYPE_TOOL_HEADER;
  art->prefsizey = HEADERY; /* XXX */
  art->init = matpro_header_region_init;
  art->draw = matpro_header_region_draw;
  art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_HEADER | ED_KEYMAP_VIEW2D;
  BLI_addhead(&st->regiontypes, art);

  WM_menutype_add(MEM_new<MenuType>(__func__, add_catalog_assets_menu_type_matpro()));
  WM_menutype_add(MEM_new<MenuType>(__func__, add_root_catalogs_menu_type_matpro()));

  BKE_spacetype_register(st);
}
