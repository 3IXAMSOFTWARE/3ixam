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
#include "DNA_material_types.h"

#include "MEM_guardedalloc.h"
 
#include "BLI_ixamlib.h"
 
#include "BKE_context.h"
#include "BKE_screen.h"
#include "BKE_main.h"
#include "BKE_material.h"

#include "GPU_immediate.h"
#include "GPU_matrix.h"
#include "GPU_state.h"
 
#include "ED_space_api.h"
#include "ED_screen.h"
 
#include "WM_api.h"
#include "WM_types.h"
 
#include "UI_interface.h"
#include "UI_resources.h"
#include "UI_view2d.h"

#define MATERIAL_GROUPS 5
#define GROUP_WIDTH 8
#define GROUP_HEIGTH 10
#define MATERIAL_HEIGTH 8

static SpaceLink *matlib_create(const ScrArea *area, const Scene *scene)
{
  ARegion *region;
  SpaceMatLib *smatlib;

  smatlib = MEM_callocN(sizeof(SpaceMatLib), "initmatlib");
  smatlib->spacetype = SPACE_MATLIB;

  /* tool region */
  region = MEM_callocN(sizeof(ARegion), "tool region for text");
  BLI_addtail(&smatlib->regionbase, region);
  region->regiontype = RGN_TYPE_TOOLS;
  region->alignment = RGN_ALIGN_RIGHT;
  
  /* main region */
  region = MEM_callocN(sizeof(ARegion), "main region for action");

  BLI_addtail(&smatlib->regionbase, region);
  region->regiontype = RGN_TYPE_WINDOW;

  region->v2d.align = V2D_ALIGN_NO_NEG_X | V2D_ALIGN_NO_NEG_Y;
  region->v2d.keeptot = V2D_KEEPTOT_BOUNDS;
  region->v2d.tot.xmin = region->v2d.tot.ymin = 0.0f;
  region->v2d.tot.xmax = GROUP_WIDTH * U.widget_unit * MATERIAL_GROUPS;
  
  region->v2d.min[0] = 0.0f;
  region->v2d.min[1] = 0.0f;

  region->v2d.max[0] = MAXFRAMEF;
  region->v2d.max[1] = 3.402823e+38;

  region->v2d.scroll = (V2D_SCROLL_BOTTOM | V2D_SCROLL_HORIZONTAL_HANDLES | V2D_SCROLL_VERTICAL_HANDLES);
  region->v2d.keepzoom = (V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y | V2D_LIMITZOOM | V2D_KEEPASPECT);
  region->v2d.minzoom = region->v2d.maxzoom = 1.0f;
//  region->v2d.keepofs = V2D_KEEPOFS_Y;
  region->v2d.flag = V2D_VIEWSYNC_AREA_VERTICAL;
  
  return (SpaceLink *)smatlib;
}

static SpaceLink *matlib_duplicate(SpaceLink *sl)
{
  SpaceMatLib *smatlib = MEM_dupallocN(sl);
  return (SpaceLink *)smatlib;
}

static void matlib_free(SpaceLink *UNUSED(sl))
{
  
}

static void matlib_init(struct wmWindowManager *UNUSED(wm), ScrArea *area)
{
  {
    ARegion *region = BKE_area_find_region_type(area, RGN_TYPE_WINDOW);
    float height = BLI_rctf_size_y(&region->v2d.cur);
    region->v2d.cur.ymax = region->v2d.tot.ymax;
    region->v2d.cur.ymin = region->v2d.tot.ymax - height;
  }
}

static void matlib_listener(const wmSpaceTypeListenerParams *params)
{
  wmWindow *window = params->window;
  ScrArea *area = params->area;
  wmNotifier *wmn = params->notifier;
  const Scene *scene = params->scene;

  switch (wmn->category) {
    case NC_SCENE:
      switch (wmn->data) {
        case ND_OB_ACTIVE:
        case ND_OB_SELECT:
        case ND_OB_VISIBLE:
          ED_area_tag_refresh(area);
          break;
      }
      break;
    case NC_SPACE:
      switch (wmn->data) {
        case ND_SPACE_MATLIB:
          ED_area_tag_refresh(area);
          break;
      }
      break;
  }
}

static void matlib_refresh(const bContext *C, ScrArea *area)
{
  wmWindowManager *wm = CTX_wm_manager(C);
  wmWindow *window = CTX_wm_window(C);
  SpaceMatLib *matlib = CTX_wm_space_matlib(C);

  /* update material preferences region visibility */
  ARegion* pref_region = BKE_area_find_region_type(area, RGN_TYPE_TOOLS);
  Object *ob = CTX_data_active_object(C);
  Material *object_mat = ob ? BKE_object_material_get(ob, ob->actcol) : NULL;

  if (matlib->active_material || object_mat) {
    pref_region->flag &= ~RGN_FLAG_HIDDEN;
  } else {
    pref_region->flag |= RGN_FLAG_HIDDEN;
  }
  
  ED_area_init(wm, window, area);
  ED_area_tag_redraw(area);
}

/* add handlers, stuff you only do once or on area/region changes */
static void matlib_main_area_init(wmWindowManager *wm, ARegion *region)
{
  UI_view2d_region_reinit(&region->v2d, V2D_COMMONVIEW_CUSTOM, region->winx, region->winy);
}
 
static void matlib_main_area_draw(const bContext *C, ARegion *region)
{
  View2D *v2d = &region->v2d;
  SpaceMatLib *matlib = CTX_wm_space_matlib(C);

  UI_view2d_view_ortho(v2d);

  /* clear and setup matrix */
  UI_ThemeClearColor(TH_BACK);

  /* Draw here */
  {
    const uiStyle *style = UI_style_get_dpi();
    const char* panel_name1 = "MATLIB_PT_main";

    uiBlock *block = UI_block_begin(C, region, __func__, UI_EMBOSS);
    uiLayout *layout = UI_block_layout(block,
                                  UI_LAYOUT_VERTICAL,
                                  UI_LAYOUT_PANEL,
                                  0,
                                  v2d->tot.ymax,
                                  BLI_rctf_size_x(&v2d->tot),
                                  1,
                                  0,
                                  style);

    struct PanelType *pt = WM_paneltype_find(panel_name1, true);
    UI_paneltype_draw((bContext *)C, pt, layout);

    UI_block_layout_resolve(block, NULL, NULL, NULL, NULL);
    v2d->tot.xmax = matlib->group_width * U.widget_unit * matlib->groups_len;
    v2d->tot.ymax = matlib->group_height * U.widget_unit * MATERIAL_HEIGTH;
    UI_block_end(C, block);
    UI_block_draw(C, block);
  }

  /* reset view matrix */
  UI_view2d_view_restore(C);

  /* scrollers */
  UI_view2d_scrollers_draw(v2d, NULL);
}

static void matlib_preferences_area_init(wmWindowManager *wm, ARegion *region)
{
  ED_region_panels_init(wm, region);
  region->v2d.keepzoom |= V2D_LOCKZOOM_X | V2D_LOCKZOOM_Y;
}

static void matlib_preferences_area_draw(const bContext *C, ARegion *region)
{
  SpaceMatLib *matlib = CTX_wm_space_matlib(C);
  ED_region_panels_ex(C, region, (const char *[]){CTX_data_mode_string(C), NULL});
}
 
/********************* registration ********************/
 
/* only called once, from space/spacetypes.c */
void ED_spacetype_matlib(void)
{
  SpaceType *st = MEM_callocN(sizeof(SpaceType), "spacetype matlib");
  ARegionType *art;

  st->spaceid = SPACE_MATLIB;
  strncpy(st->name, "MatLib", BKE_ST_MAXNAME);
 
  st->create = matlib_create;
  st->duplicate = matlib_duplicate;
  st->init = matlib_init;
  st->listener = matlib_listener;
  st->refresh = matlib_refresh;
//  st->free = matlib_free;
//  st->operatortypes = matlib_operatortypes;
//  st->keymap = matlib_keymap;
//  st->dropboxes = matlib_dropboxes;
  
	/* regions: main window */
	art = MEM_callocN(sizeof(ARegionType), "spacetype material library main region");
	art->regionid = RGN_TYPE_WINDOW;
	art->init = matlib_main_area_init;
	art->draw = matlib_main_area_draw;
  art->keymapflag = ED_KEYMAP_VIEW2D | ED_KEYMAP_UI;
	BLI_addhead(&st->regiontypes, art);
  
  /* regions: material preferences */
  art = MEM_callocN(sizeof(ARegionType), "spacetype material library tools region");
  art->regionid = RGN_TYPE_TOOLS;
  art->prefsizex = 300;
  art->keymapflag = ED_KEYMAP_UI;
  art->init = matlib_preferences_area_init;
  art->draw = matlib_preferences_area_draw;
  BLI_addhead(&st->regiontypes, art);
 
	BKE_spacetype_register(st);
}
