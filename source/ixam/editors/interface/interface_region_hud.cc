

/** \file
 * \ingroup edinterface
 *
 * Floating Persistent Region
 */

#include <cstring>

#include "MEM_guardedalloc.h"

#include "DNA_screen_types.h"
#include "DNA_userdef_types.h"

#include "BLI_listbase.h"
#include "BLI_rect.h"
#include "BLI_string.h"
#include "BLI_utildefines.h"

#include "BKE_context.h"
#include "BKE_screen.h"

#include "WM_api.h"
#include "WM_types.h"

#include "RNA_access.h"

#include "UI_interface.h"
#include "UI_view2d.h"

#include "BLT_translation.h"

#include "ED_screen.h"
#include "ED_undo.h"

#include "GPU_framebuffer.h"
#include "interface_intern.h"

/* -------------------------------------------------------------------- */
/** \name Utilities
 * \{ */

struct HudRegionData {
  short regionid;
};

static bool last_redo_poll(const bContext *C, short region_type)
{
  wmOperator *op = WM_operator_last_redo(C);
  if (op == nullptr) {
    return false;
  }

  bool success = false;
  {
    /* Make sure that we are using the same region type as the original
     * operator call. Otherwise we would be polling the operator with the
     * wrong context.
     */
    ScrArea *area = CTX_wm_area(C);
    ARegion *region_op = (region_type != -1) ? BKE_area_find_region_type(area, region_type) :
                                               nullptr;
    ARegion *region_prev = CTX_wm_region(C);
    CTX_wm_region_set((bContext *)C, region_op);

    if (WM_operator_repeat_check(C, op) && WM_operator_check_ui_empty(op->type) == false) {
      success = WM_operator_poll((bContext *)C, op->type);
    }
    CTX_wm_region_set((bContext *)C, region_prev);
  }
  return success;
}

static void hud_region_hide(ARegion *region)
{
  region->flag |= RGN_FLAG_HIDDEN;
  /* Avoids setting 'AREA_FLAG_REGION_SIZE_UPDATE'
   * since other regions don't depend on this. */
  BLI_rcti_init(&region->winrct, 0, 0, 0, 0);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Redo Panel
 * \{ */

static bool hud_panel_operator_redo_poll(const bContext *C, PanelType * /*pt*/)
{
  ScrArea *area = CTX_wm_area(C);
  ARegion *region = BKE_area_find_region_type(area, RGN_TYPE_HUD);
  if (region != nullptr) {
    HudRegionData *hrd = static_cast<HudRegionData *>(region->regiondata);
    if (hrd != nullptr) {
      return last_redo_poll(C, hrd->regionid);
    }
  }
  return false;
}

static void hud_panel_operator_redo_draw_header(const bContext *C, Panel *panel)
{
  wmOperator *op = WM_operator_last_redo(C);
  BLI_strncpy(panel->drawname, WM_operatortype_name(op->type, op->ptr), sizeof(panel->drawname));
}

static void hud_panel_operator_redo_draw(const bContext *C, Panel *panel)
{
  wmOperator *op = WM_operator_last_redo(C);
  if (op == nullptr) {
    return;
  }
  if (!WM_operator_check_ui_enabled(C, op->type->name)) {
    uiLayoutSetEnabled(panel->layout, false);
  }
  uiLayout *col = uiLayoutColumn(panel->layout, false);
  uiTemplateOperatorRedoProperties(col, C);
}

static void hud_panels_register(ARegionType *art, int space_type, int region_type)
{
  PanelType *pt = MEM_cnew<PanelType>(__func__);
  strcpy(pt->idname, "OPERATOR_PT_redo");
  strcpy(pt->label, N_("Redo"));
  strcpy(pt->translation_context, BLT_I18NCONTEXT_DEFAULT_BPYRNA);
  pt->draw_header = hud_panel_operator_redo_draw_header;
  pt->draw = hud_panel_operator_redo_draw;
  pt->poll = hud_panel_operator_redo_poll;
  pt->space_type = space_type;
  pt->region_type = region_type;
  pt->flag |= PANEL_TYPE_DEFAULT_CLOSED;
  BLI_addtail(&art->paneltypes, pt);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Callbacks for Floating Region
 * \{ */

static void hud_region_init(wmWindowManager *wm, ARegion *region)
{
  ED_region_panels_init(wm, region);
  
  region->alignment = RGN_ALIGN_BOTTOM_RIGHT;
  region->v2d.minzoom = 1.0f;
  region->v2d.maxzoom = 1.0f;
  region->flag |= RGN_FLAG_DYNAMIC_SIZE;
}

static void hud_region_free(ARegion *region)
{
  MEM_SAFE_FREE(region->regiondata);
}

static void hud_region_draw(const bContext *C, ARegion *region)
{
  ED_region_panels_layout(C, region); 
  ED_region_panels_draw(C, region);
}

static void view3d_hud_region_listener(const wmRegionListenerParams *params)
{
  ARegion *region = params->region;
  const wmNotifier *wmn = params->notifier;
  
  /* context changes */
  switch (wmn->category) {
    case NC_SCENE:
      if (ELEM(wmn->data, ND_OB_ACTIVE)) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_OBJECT:
      if (ELEM(wmn->data, ND_TRANSFORM)) {
        ED_region_tag_redraw(region);
      }
      break;
    case NC_SPACE:
      if (ELEM(wmn->data, ND_SPACE_VIEW3D)) {
        ED_region_tag_refresh_ui(region);
      }
      break;      
  }
}

ARegionType *ED_area_type_hud(int space_type)
{
  ARegionType *art = MEM_cnew<ARegionType>(__func__);
  art->regionid = RGN_TYPE_HUD;
  art->keymapflag = ED_KEYMAP_UI | ED_KEYMAP_VIEW2D;
  art->draw = hud_region_draw;
  art->init = hud_region_init;
  art->free = hud_region_free;
  art->listener = view3d_hud_region_listener;
  art->message_subscribe = ED_region_generic_tools_region_message_subscribe;
  return art;
}

static ARegion *hud_region_add(ScrArea *area)
{
  ARegion *region = MEM_cnew<ARegion>(__func__);
  ARegion *region_win = BKE_area_find_region_type(area, RGN_TYPE_WINDOW);
  if (region_win) {
    BLI_insertlinkbefore(&area->regionbase, region_win, region);
  }
  else {
    BLI_addtail(&area->regionbase, region);
  }
  region->regiontype = RGN_TYPE_HUD;
  region->alignment = RGN_ALIGN_FLOAT;
  region->overlap = true;
  region->flag |= RGN_FLAG_DYNAMIC_SIZE;

  if (region_win) {
    float x, y;

    UI_view2d_scroller_size_get(&region_win->v2d, true, &x, &y);
    region->runtime.offset_x = x;
    region->runtime.offset_y = y;
  }

  return region;
}

void ED_area_type_hud_clear(wmWindowManager *wm, ScrArea *area_keep)
{
  LISTBASE_FOREACH (wmWindow *, win, &wm->windows) {
    bScreen *screen = WM_window_get_active_screen(win);
    LISTBASE_FOREACH (ScrArea *, area, &screen->areabase) {
      if (area != area_keep) {
        LISTBASE_FOREACH (ARegion *, region, &area->regionbase) {
          if (region->regiontype == RGN_TYPE_HUD) {
            if ((region->flag & RGN_FLAG_HIDDEN) == 0) {
              hud_region_hide(region);
              ED_region_tag_redraw(region);
              ED_area_tag_redraw(area);
            }
          }
        }
      }
    }
  }
}

void ED_area_type_hud_ensure(bContext *C, ScrArea *area)
{
  wmWindowManager *wm = CTX_wm_manager(C);
  ED_area_type_hud_clear(wm, area);

  ARegionType *art = BKE_regiontype_from_id(area->type, RGN_TYPE_HUD);
  if (art == nullptr) {
    return;
  }

  ARegion *region = BKE_area_find_region_type(area, RGN_TYPE_HUD);

  if (region && (region->flag & RGN_FLAG_HIDDEN_BY_USER)) {
    /* The region is intentionally hidden by the user, don't show it. */
    hud_region_hide(region);
    return;
  }

  bool init = false;
  const bool was_hidden = region == nullptr || region->visible == false;
  ARegion *region_op = CTX_wm_region(C);
  BLI_assert((region_op == nullptr) || (region_op->regiontype != RGN_TYPE_HUD));
  if (!last_redo_poll(C, region_op ? region_op->regiontype : -1)) {
    if (region) {
      ED_region_tag_redraw(region);
      hud_region_hide(region);
    }
    return;
  }

  if (region == nullptr) {
    init = true;
    region = hud_region_add(area);
    region->type = art;
  }

  /* Let 'ED_area_update_region_sizes' do the work of placing the region.
   * Otherwise we could set the 'region->winrct' & 'region->winx/winy' here. */
  if (init) {
    area->flag |= AREA_FLAG_REGION_SIZE_UPDATE;
  }
  else {
    if (region->flag & RGN_FLAG_HIDDEN) {
      /* Also forces recalculating HUD size in hud_region_layout(). */
      area->flag |= AREA_FLAG_REGION_SIZE_UPDATE;
    }
    region->flag &= ~RGN_FLAG_HIDDEN;
  }

  {
    HudRegionData *hrd = static_cast<HudRegionData *>(region->regiondata);
    if (hrd == nullptr) {
      hrd = MEM_cnew<HudRegionData>(__func__);
      region->regiondata = hrd;
    }
    if (region_op) {
      hrd->regionid = region_op->regiontype;
    }
    else {
      hrd->regionid = -1;
    }
  }

  if (init) {
    /* This is needed or 'winrct' will be invalid. */
    wmWindow *win = CTX_wm_window(C);
    ED_area_update_region_sizes(wm, win, area);
  }

  ED_region_floating_init(region);
  ED_region_tag_redraw(region);

  /* Reset zoom level (not well supported). */
  rctf reset_rect = {};
  reset_rect.xmax = region->winx;
  reset_rect.ymax = region->winy;
  region->v2d.cur = region->v2d.tot = reset_rect;
  region->v2d.minzoom = 1.0f;
  region->v2d.maxzoom = 1.0f;

  region->visible = !(region->flag & RGN_FLAG_HIDDEN);

  /* We shouldn't need to do this every time :S */
  /* XXX, this is evil! - it also makes the menu show on first draw. :( */
  if (region->visible) {
    ARegion *region_prev = CTX_wm_region(C);
    CTX_wm_region_set((bContext *)C, region);
    ED_region_panels_layout(C, region);
    if (was_hidden) {
      region->winx = region->v2d.winx;
      region->winy = region->v2d.winy;
      region->v2d.cur = region->v2d.tot = reset_rect;
    }
    CTX_wm_region_set((bContext *)C, region_prev);
  }

  region->visible = !((region->flag & RGN_FLAG_HIDDEN) || (region->flag & RGN_FLAG_TOO_SMALL));
}

/** \} */
