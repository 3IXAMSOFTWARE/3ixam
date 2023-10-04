/*
 * ***** BEGIN GPL LICENSE BLOCK *****
 *

 *
 *
 * Contributor(s): Michael Neilly
 *
 * ***** END GPL LICENSE BLOCK *****
 */
 
/** \file ixam/editors/space_matlib/space_matlib.c
 *  \ingroup spmatlib
 */
 
#include <stdio.h>
#include <string.h>
 
#include "DNA_text_types.h"
#include "DNA_scene_types.h"
#include "DNA_image_types.h"
#include "DNA_mask_types.h"
#include "DNA_object_types.h"
 
#include "MEM_guardedalloc.h"
 
#include "BLI_ixamlib.h"
#include "BLI_math.h"
#include "BLI_threads.h"

#include "BLO_read_write.h"
 
#include "BKE_colortools.h"
#include "BKE_context.h"
#include "BKE_image.h"
#include "BKE_layer.h"
#include "BKE_lib_id.h"
#include "BKE_lib_remap.h"
#include "BKE_screen.h"
 
#include "IMB_imbuf_types.h"

#include "ED_space_api.h"
#include "ED_screen.h"
#include "ED_image.h"
#include "ED_mask.h"
#include "ED_node.h"
#include "ED_render.h"
#include "ED_transform.h"
#include "ED_util.h"
#include "ED_uvedit.h"

#include "WM_api.h"
#include "WM_types.h"
 
#include "UI_interface.h"
#include "UI_resources.h"
#include "UI_view2d.h"

#include "RNA_access.h"
#include "RNA_enum_types.h"

#include "DRW_engine.h"

#include "../space_image/image_intern.h"
#include "space_render_intern.h"
 
#define PROGRESS_PANEL_HEIGHT ((UI_UNIT_Y + UI_style_get_dpi()->buttonspacey) * 3)

static SpaceLink *render_create(const ScrArea *area, const Scene *scene)
{
  ARegion *region;
  SpaceRender *srender;
  srender = MEM_callocN(sizeof(SpaceRender), "init SpaceRender");
  srender->spacetype = SPACE_RENDER;
  srender->zoom = 1.0f;
  srender->lock = true;
  srender->flag = SI_SHOW_GPENCIL | SI_USE_ALPHA | SI_COORDFLOATS;
  srender->uv_opacity = 1.0f;
  srender->overlay.flag = SI_OVERLAY_SHOW_OVERLAYS;
  srender->yof = -PROGRESS_PANEL_HEIGHT * 2;
  
  BKE_imageuser_default(&srender->iuser);
  srender->iuser.flag = IMA_SHOW_STEREO | IMA_ANIM_ALWAYS;

  BKE_scopes_new(&srender->scopes);
  srender->sample_line_hist.height = 100;

  srender->tile_grid_shape[0] = 1;
  srender->tile_grid_shape[1] = 1;

  srender->custom_grid_subdiv = 10;
  
  region = MEM_callocN(sizeof(ARegion), "render menu region");
  BLI_addtail(&srender->regionbase, region);
  region->regiontype = RGN_TYPE_PRO_MENU;
  region->alignment = RGN_ALIGN_RIGHT;
  region->v2d.align = V2D_ALIGN_NO_NEG_X;
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.keeptot = V2D_KEEPTOT_STRICT;
  region->v2d.maxzoom = region->v2d.minzoom = 1.0f;
  
  region = MEM_callocN(sizeof(ARegion), "contorl region for render");
  BLI_addtail(&srender->regionbase, region);
  region->regiontype = RGN_TYPE_TEMPORARY;
  region->alignment = RGN_ALIGN_TOP;
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.keepofs = V2D_LOCKOFS_X | V2D_LOCKOFS_Y;
  region->v2d.keeptot = V2D_KEEPTOT_BOUNDS;
  region->v2d.maxzoom = region->v2d.minzoom = 1.0f;
  
  region = MEM_callocN(sizeof(ARegion), "main region for render");
  BLI_addtail(&srender->regionbase, region);
  region->regiontype = RGN_TYPE_WINDOW;
  region->alignment = RGN_ALIGN_TOP;
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.keeptot = V2D_KEEPTOT_STRICT;
  region->v2d.maxzoom = region->v2d.minzoom = 1.0f;
  
  region = MEM_callocN(sizeof(ARegion), "render stats region");
  BLI_addtail(&srender->regionbase, region);
  region->regiontype = RGN_TYPE_EXECUTE;
  region->alignment = RGN_ALIGN_RIGHT;
  region->v2d.scroll = (V2D_SCROLL_RIGHT | V2D_SCROLL_BOTTOM);
  region->v2d.align = V2D_ALIGN_NO_NEG_X;
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.keeptot = V2D_KEEPTOT_STRICT;
  region->v2d.maxzoom = region->v2d.minzoom = 1.0f;
  
  region = MEM_callocN(sizeof(ARegion), "render post effects region");
  BLI_addtail(&srender->regionbase, region);
  region->regiontype = RGN_TYPE_TOOL_PROPS;
  region->v2d.scroll = (V2D_SCROLL_RIGHT | V2D_SCROLL_BOTTOM);
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.keeptot = V2D_KEEPTOT_STRICT;
  region->v2d.maxzoom = region->v2d.minzoom = 1.0f;
  
  return (SpaceLink *)srender;
}

static SpaceLink *render_duplicate(SpaceLink *sl)
{
  SpaceRender *srender = MEM_dupallocN(sl);
  BKE_scopes_new(&srender->scopes);
  return (SpaceLink *)srender;
}

static void render_refresh(const bContext *C, ScrArea *area)
{
  Scene *scene = CTX_data_scene(C);
  SpaceRender *srender = CTX_wm_space_render(C);
  Image *ima;

  ima = ED_space_image((SpaceImage *)srender);
  BKE_image_user_frame_calc(ima, &srender->iuser, scene->r.cfra);

  /* Check if we have to set the image from the edit-mesh. */
  if (ima && ima->type == IMA_TYPE_R_RESULT) {
    if (scene->nodetree) {
      ED_node_composite_job(C, scene->nodetree, scene);
    }
  }
}

static void render_operatortypes(void)
{
  WM_operatortype_append(RENDER_OT_save);
  WM_operatortype_append(RENDER_OT_save_as);
}

static void image_scopes_tag_refresh(ScrArea *area)
{
  SpaceImage *sima = (SpaceImage *)area->spacedata.first;
  ARegion *region;

  /* only while histogram is visible */
  for (region = area->regionbase.first; region; region = region->next) {
    if (region->regiontype == RGN_TYPE_TOOL_PROPS && region->flag & RGN_FLAG_HIDDEN) {
      return;
    }
  }

  sima->scopes.ok = 0;
}

static void render_listener(const wmSpaceTypeListenerParams *params)
{
  wmWindow *win = params->window;
  ScrArea *area = params->area;
  wmNotifier *wmn = params->notifier;
  SpaceImage *sima = (SpaceImage *)area->spacedata.first;

  /* context changes */
  switch (wmn->category) {
    case NC_WINDOW:
      /* notifier comes from editing color space */
      image_scopes_tag_refresh(area);
      ED_area_tag_redraw(area);
      break;
    case NC_SCENE:
      switch (wmn->data) {
        case ND_FRAME:
        case ND_NODES:
          image_scopes_tag_refresh(area);
          ED_area_tag_refresh(area);
          ED_area_tag_redraw(area);
          break;
        case ND_MODE:
          if (wmn->subtype == NS_EDITMODE_MESH) {
            ED_area_tag_refresh(area);
          }
          ED_area_tag_redraw(area);
          break;
        case ND_RENDER_RESULT:
        case ND_RENDER_OPTIONS:
        case ND_COMPO_RESULT:
          if (ED_space_image_show_render(sima)) {
            image_scopes_tag_refresh(area);
          }
          ED_area_tag_redraw(area);
          break;
      }
      break;
    case NC_SPACE:
      if (wmn->data == ND_SPACE_IMAGE) {
        image_scopes_tag_refresh(area);
        ED_area_tag_redraw(area);
      }
      break;
    case NC_MASK: {
      ViewLayer *view_layer = WM_window_get_active_view_layer(win);
      Object *obedit = BKE_view_layer_edit_object_get(view_layer);
      if (ED_space_image_check_show_maskedit(sima, obedit)) {
        switch (wmn->data) {
          case ND_SELECT:
            ED_area_tag_redraw(area);
            break;
          case ND_DATA:
          case ND_DRAW:
            /* causes node-recalc */
            ED_area_tag_redraw(area);
            ED_area_tag_refresh(area);
            break;
        }
        switch (wmn->action) {
          case NA_SELECTED:
            ED_area_tag_redraw(area);
            break;
          case NA_EDITED:
            /* causes node-recalc */
            ED_area_tag_redraw(area);
            ED_area_tag_refresh(area);
            break;
        }
      }
      break;
    }
    case NC_GEOM: {
      switch (wmn->data) {
        case ND_DATA:
        case ND_SELECT:
          image_scopes_tag_refresh(area);
          ED_area_tag_refresh(area);
          ED_area_tag_redraw(area);
          break;
      }
      break;
    }
    case NC_OBJECT: {
      switch (wmn->data) {
        case ND_TRANSFORM:
        case ND_MODIFIER: {
          ViewLayer *view_layer = WM_window_get_active_view_layer(win);
          Object *ob = BKE_view_layer_active_object_get(view_layer);
          if (ob && (ob == wmn->reference) && (ob->mode & OB_MODE_EDIT)) {
            if (sima->lock && (sima->flag & SI_DRAWSHADOW)) {
              ED_area_tag_refresh(area);
              ED_area_tag_redraw(area);
            }
          }
          break;
        }
      }

      break;
    }
    case NC_ID: {
      if (wmn->action == NA_RENAME) {
        ED_area_tag_redraw(area);
      }
      break;
    }
    case NC_WM:
      if (wmn->data == ND_UNDO) {
        ED_area_tag_redraw(area);
        ED_area_tag_refresh(area);
      }
      break;
  }
}

static void render_init(struct wmWindowManager *UNUSED(wm), struct ScrArea *area)
{

}

static void render_image_fit_in_view(struct SpaceRender *srender, struct ARegion *region)
{
  float offset_factor = PROGRESS_PANEL_HEIGHT / ((float)BLI_rcti_size_y(&region->winrct));
  region->winrct.ymin += PROGRESS_PANEL_HEIGHT;

  float aspx, aspy, zoomx, zoomy, w, h;
  int width, height;

  ED_space_image_get_size((SpaceImage *)srender, &width, &height);
  ED_space_image_get_aspect((SpaceImage *)srender, &aspx, &aspy);

  w = width * aspx;
  h = height * aspy;

  /* check if the image will fit in the image with (zoom == 1) */
  width = BLI_rcti_size_x(&region->winrct) + 1;
  height = BLI_rcti_size_y(&region->winrct) + 1;


  zoomx = (float)width / w;
  zoomy = (float)height / h;

  float oldzoom = srender->zoom;

  srender->zoom = min_ff(zoomx, zoomy);

  if (srender->zoom < 0.1f || srender->zoom > 4.0f) {
    /* check zoom limits */
    ED_space_image_get_size((SpaceImage *)srender, &width, &height);

    width *= srender->zoom;
    height *= srender->zoom;

    if ((width < 4) && (height < 4) && srender->zoom < oldzoom) {
      srender->zoom = oldzoom;
    }
    else if (BLI_rcti_size_x(&region->winrct) <= srender->zoom) {
      srender->zoom = oldzoom;
    }
    else if (BLI_rcti_size_y(&region->winrct) <= srender->zoom) {
      srender->zoom = oldzoom;
    }
  }
  srender->xof = 0.0f;
  srender->yof = -(h * offset_factor * 1.1f) / 2;
  region->winrct.ymin -= PROGRESS_PANEL_HEIGHT;
}

/* add handlers, stuff you only do once or on area/region changes */
static void render_main_area_init(wmWindowManager *wm, ARegion *region)
{
  UI_view2d_region_reinit(&region->v2d, V2D_COMMONVIEW_PANELS_UI, region->winx, region->winy);
}

static void render_main_region_listener(const wmRegionListenerParams *params)
{
  ScrArea *area = params->area;
  ARegion *region = params->region;
  wmNotifier *wmn = params->notifier;

  /* context changes */
  switch (wmn->category) {
    case NC_GEOM:
      if (ELEM(wmn->data, ND_DATA, ND_SELECT)) {
        WM_gizmomap_tag_refresh(region->gizmo_map);
      }
      break;
    case NC_GPENCIL:
      if (ELEM(wmn->action, NA_EDITED, NA_SELECTED)) {
        ED_region_tag_redraw(region);
      }
      else if (wmn->data & ND_GPENCIL_EDITMODE) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_IMAGE:
      ED_region_tag_redraw(region);
      break;
    case NC_MATERIAL:
      if (wmn->data == ND_SHADING_LINKS) {
        SpaceImage *sima = area->spacedata.first;

        if (sima->iuser.scene && (sima->iuser.scene->toolsettings->uv_flag & UV_SHOW_SAME_IMAGE)) {
          ED_region_tag_redraw(region);
        }
      }
      break;
    case NC_SCREEN:
      if (ELEM(wmn->data, ND_LAYER)) {
        ED_region_tag_redraw(region);
      }
      break;
  }
}

static void render_user_refresh_scene(const bContext *C, SpaceRender *srender)
{
  /* Update scene image user for acquiring render results. */
  srender->iuser.scene = CTX_data_scene(C);

  if (srender->image && srender->image->type == IMA_TYPE_R_RESULT) {
    /* While rendering, prefer scene that is being rendered. */
    Scene *render_scene = ED_render_job_get_current_scene(C);
    if (render_scene) {
      srender->iuser.scene = render_scene;
    }
  }

  /* Auto switch image to show in UV editor when selection changes. */
  ED_space_image_auto_set(C, (SpaceImage *)srender);
}

static void render_main_region_set_view2d(SpaceRender *srender, ARegion *region)
{
  Image *ima = ED_space_image((SpaceImage *)srender);

  int width, height;
  ED_space_image_get_size((SpaceImage *)srender, &width, &height);

  float w = width;
  float h = height;

  if (ima) {
    h *= ima->aspy / ima->aspx;
  }

  int winx = BLI_rcti_size_x(&region->winrct) + 1;
  int winy = BLI_rcti_size_y(&region->winrct) + 1;

  /* For region overlap, move center so image doesn't overlap header. */
  const rcti *visible_rect = ED_region_visible_rect(region);
  const int visible_winy = BLI_rcti_size_y(visible_rect) + 1;
  int visible_centerx = 0;
  int visible_centery = visible_rect->ymin + (visible_winy - winy) / 2;

  region->v2d.tot.xmin = 0;
  region->v2d.tot.ymin = 0;
  region->v2d.tot.xmax = w;
  region->v2d.tot.ymax = h;

  region->v2d.mask.xmin = region->v2d.mask.ymin = 0;
  region->v2d.mask.xmax = winx;
  region->v2d.mask.ymax = winy;

  /* which part of the image space do we see? */
  float x1 = region->winrct.xmin + visible_centerx + (winx - srender->zoom * w) / 2.0f;
  float y1 = region->winrct.ymin + visible_centery + (winy - srender->zoom * h) / 2.0f;

  x1 -= srender->zoom * srender->xof;
  y1 -= srender->zoom * srender->yof;

  /* relative display right */
  region->v2d.cur.xmin = ((region->winrct.xmin - (float)x1) / srender->zoom);
  region->v2d.cur.xmax = region->v2d.cur.xmin + ((float)winx / srender->zoom);

  /* relative display left */
  region->v2d.cur.ymin = ((region->winrct.ymin - (float)y1) / srender->zoom);
  region->v2d.cur.ymax = region->v2d.cur.ymin + ((float)winy / srender->zoom);

  /* normalize 0.0..1.0 */
  region->v2d.cur.xmin /= w;
  region->v2d.cur.xmax /= w;
  region->v2d.cur.ymin /= h;
  region->v2d.cur.ymax /= h;
}

static void render_main_area_draw(const bContext *C, ARegion *region)
{
  /* draw entirely, view changes should be handled here */
  SpaceRender *srender = CTX_wm_space_render(C);
//  Object *obedit = CTX_data_edit_object(C);
//  struct Depsgraph *depsgraph = CTX_data_expect_evaluated_depsgraph(C);
  Scene *scene = CTX_data_scene(C);
  View2D *v2d = &region->v2d;
  rctf old_cur;
  memcpy(&old_cur, &v2d->cur, sizeof(v2d->cur));
  Image *image = ED_space_image((SpaceImage *)srender);
  const bool show_viewer = (image && image->source == IMA_SRC_VIEWER);

  /* XXX not supported yet, disabling for now */
  scene->r.scemode &= ~R_COMP_CROP;

  render_user_refresh_scene(C, srender);
  {
    render_image_fit_in_view(srender, region);
  }
  /* we set view2d from own zoom and offset each time */
  render_main_region_set_view2d(srender, region);

  /* check for mask (delay draw) */

  if (show_viewer) {
    BLI_thread_lock(LOCK_DRAW_IMAGE);
  }
  DRW_draw_view(C, NULL);
  if (show_viewer) {
    BLI_thread_unlock(LOCK_DRAW_IMAGE);
  }
  {
//    float col[4];
//    UI_GetThemeColor4fv(TH_BACK, col);
//    UI_draw_roundbox_4fv(&(const rctf) {
//      .xmin = 0.0f,
//      .xmax = region->winx,
//      .ymin = 0,
//      .ymax = PROGRESS_PANEL_HEIGHT,
//    }, true, 0, col);
    uiBlock *block = UI_block_begin(C, region, "ProgressPanelBlock", UI_EMBOSS);
    struct PanelType *pt = WM_paneltype_find("RENDER_PT_progress_bar", true);
    uiLayout *layout = UI_block_layout(block,
                                       UI_LAYOUT_VERTICAL,
                                       UI_LAYOUT_PANEL,
                                       0,
                                       PROGRESS_PANEL_HEIGHT,
                                       region->winx,
                                       1,
                                       0,
                                       UI_style_get_dpi());
    UI_paneltype_draw((bContext *)C, pt, layout);
    UI_block_layout_resolve(block, NULL, NULL, NULL, NULL);
    UI_block_draw(C, block);
  }
  v2d->cur = old_cur;
}


static void render_menu_area_init(wmWindowManager *wm, ARegion *region)
{
  ED_region_panels_init(wm, region);
  region->v2d.keepzoom |= V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y;
}

static void render_menu_region_layout(const bContext *C, ARegion *region)
{
  SpaceRender *srender = CTX_wm_space_render(C);
  char id_lower[64];
  const char *contexts[2] = {id_lower, NULL};

  /* Avoid duplicating identifiers, use existing RNA enum. */
  {
    const EnumPropertyItem *items = rna_enum_render_common_preference_section_items;
    int i = RNA_enum_from_value(items, srender->menu_section_active);
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

static void render_post_effects_region_layout(const bContext *C, ARegion *region)
{
  SpaceRender *srender = CTX_wm_space_render(C);
  char id_lower[64];
  const char *contexts[2] = {id_lower, NULL};

  /* Avoid duplicating identifiers, use existing RNA enum. */
  {
    const EnumPropertyItem *items = rna_enum_render_post_effects_section_items;
    int i = RNA_enum_from_value(items, srender->post_section_active);
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

static void render_statistic_region_layout(const bContext *C, ARegion *region)
{
  SpaceRender *srender = CTX_wm_space_render(C);
  char id_lower[64];
  const char *contexts[2] = {id_lower, NULL};

  /* Avoid duplicating identifiers, use existing RNA enum. */
  {
    const EnumPropertyItem *items = rna_enum_render_statistics_section_items;
    int i = RNA_enum_from_value(items, srender->statistic_section_active);
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

static void render_region_draw(const bContext *C, ARegion *region)
{
  ED_region_panels_draw(C, region);
}

static uiBlock *wm_block_create_view_info(const bContext *C, ARegion *region)
{
  ScrArea *ctx_area = CTX_wm_area(C);
  
  const int padding = 5;
  rcti rect;
  rect.xmin = 0;
  rect.xmax = region->winx;
  rect.ymin = region->winy - padding;
  if (region->winrct.ymax > 2.0f * BLI_rcti_size_y(&ctx_area->totrct) / 3.0f) {
    rect.ymin -= 80 * UI_DPI_FAC;
  }
  
  const uiStyle *style = UI_style_get_dpi();
  const char* panel_name = "RENDER_PT_image_properties";

  uiBlock *block = UI_block_begin(C, region, __func__, UI_EMBOSS);
  uiLayout *layout = UI_block_layout(block,
                                     UI_LAYOUT_VERTICAL,
                                     UI_LAYOUT_HEADER,
                                     rect.xmin,
                                     rect.ymin,
                                     BLI_rcti_size_x(&rect),
                                     1,
                                     0,
                                     style);
  
  struct PanelType *pt = WM_paneltype_find(panel_name, true);
  UI_paneltype_draw((bContext *)C, pt, layout);
  
  UI_block_layout_resolve(block, NULL, NULL, NULL, NULL);
  UI_block_end(C, block);
  
  return block;
}

static void render_control_region_draw(const bContext *C, ARegion *region)
{
  ED_region_panels_ex(C, region, (const char *[]){CTX_data_mode_string(C), NULL});

  //uiBlock* block = wm_block_create_view_info(C, region);
  //UI_block_draw(C, block);
}

static void render_control_region_listener(const wmRegionListenerParams *params)
{
  ScrArea *area = params->area;
  ARegion *region = params->region;
  wmNotifier *wmn = params->notifier;

  /* context changes */
  switch (wmn->category) {
    case NC_SCENE:
    case NC_IMAGE:
      ED_region_tag_redraw(region);
      break;
    case NC_SCREEN:
      if (ELEM(wmn->data, ND_LAYER)) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_SPACE:
      if (wmn->data == ND_SPACE_RENDER) {
        image_scopes_tag_refresh(area);
        ED_region_tag_redraw(region);
      }
      break;
  }
}
static void srender_ixam_read_data(IxamDataReader *UNUSED(reader), SpaceLink *sl)
{
  SpaceRender *srender = (SpaceRender *)sl;

  srender->iuser.scene = NULL;
  srender->scopes.waveform_1 = NULL;
  srender->scopes.waveform_2 = NULL;
  srender->scopes.waveform_3 = NULL;
  srender->scopes.vecscope = NULL;
  srender->scopes.ok = 0;
}

static void srender_ixam_read_lib(IxamLibReader *reader, ID *parent_id, SpaceLink *sl)
{
  SpaceRender *srender = (SpaceRender *)sl;

  BLO_read_id_address(reader, parent_id->lib, &srender->image);
  BLO_read_id_address(reader, parent_id->lib, &srender->mask_info.mask);

  /* NOTE: pre-2.5, this was local data not lib data, but now we need this as lib data
   * so fingers crossed this works fine!
   */
  BLO_read_id_address(reader, parent_id->lib, &srender->gpd);
}

static void srender_ixam_write(IxamWriter *writer, SpaceLink *sl)
{
  BLO_write_struct(writer, SpaceRender, sl);
}

/* only called once, from space/spacetypes.c */
void ED_spacetype_render(void)
{
  SpaceType *st = MEM_callocN(sizeof(SpaceType), "spacetype render");
  ARegionType *art;

  st->spaceid = SPACE_RENDER;
  strncpy(st->name, "Render", BKE_ST_MAXNAME);
 
  st->create = render_create;
  st->duplicate = render_duplicate;
  st->listener = render_listener;
  st->init = render_init;
  st->refresh = render_refresh;
  st->operatortypes = render_operatortypes;
  st->ixam_read_data = srender_ixam_read_data;
  st->ixam_read_lib = srender_ixam_read_lib;
  st->ixam_write = srender_ixam_write;
  
  /* regions: main window */
  art = MEM_callocN(sizeof(ARegionType), "spacetype render main region");
  art->regionid = RGN_TYPE_WINDOW;
  art->keymapflag = ED_KEYMAP_UI;
  art->init = render_main_area_init;
  art->draw = render_main_area_draw;
  art->listener = render_main_region_listener;
  art->prefsizey = 400;
  BLI_addhead(&st->regiontypes, art);
  
  art = MEM_callocN(sizeof(ARegionType), "spacetype render control region");
  art->regionid = RGN_TYPE_TEMPORARY;
  art->keymapflag = ED_KEYMAP_UI;
  art->init = render_menu_area_init;
  art->draw = render_control_region_draw;
  art->listener = render_control_region_listener;
  art->prefsizey = 75;
  BLI_addhead(&st->regiontypes, art);
  
	art = MEM_callocN(sizeof(ARegionType), "spacetype render menu region");
  art->regionid = RGN_TYPE_PRO_MENU;
  art->keymapflag = ED_KEYMAP_UI;
	art->init = render_menu_area_init;
	art->draw = render_region_draw;
  art->layout = render_menu_region_layout;
  art->prefsizex = 450;
	BLI_addhead(&st->regiontypes, art);

  art = MEM_callocN(sizeof(ARegionType), "spacetype render stats region");
  art->regionid = RGN_TYPE_EXECUTE;
  art->init = render_menu_area_init;
  art->draw = render_region_draw;
  art->layout = render_statistic_region_layout;
  art->keymapflag = ED_KEYMAP_UI;
  art->prefsizex = 300;
  BLI_addhead(&st->regiontypes, art);
  
  art = MEM_callocN(sizeof(ARegionType), "spacetype render post effects region");
  art->regionid = RGN_TYPE_TOOL_PROPS;
  art->init = render_menu_area_init;
  art->draw = render_region_draw;
  art->layout = render_post_effects_region_layout;
  art->keymapflag = ED_KEYMAP_UI;
  BLI_addhead(&st->regiontypes, art);
  
	BKE_spacetype_register(st);
}
