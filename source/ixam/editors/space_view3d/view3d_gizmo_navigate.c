

#include "BLI_math.h"
#include "BLI_utildefines.h"

#include "BKE_context.h"

#include "DNA_object_types.h"

#include "ED_gizmo_library.h"
#include "ED_screen.h"

#include "UI_interface.h"
#include "UI_resources.h"

#include "MEM_guardedalloc.h"

#include "RNA_access.h"

#include "WM_api.h"
#include "WM_types.h"

#include "view3d_intern.h" /* own include */

/* -------------------------------------------------------------------- */
/** \name View3D Navigation Gizmo Group
 * \{ */

/* Size of main icon. */
#define GIZMO_SIZE U.gizmo_size_navigate_v3d

/* Main gizmo offset from screen edges in unscaled pixels. */
#define GIZMO_OFFSET 20.0f

/* Width of smaller buttons in unscaled pixels. */
#define GIZMO_MINI_SIZE 28.0f

/* Margin around the smaller buttons. */
#define GIZMO_MINI_OFFSET 2.0f

struct NavigateGizmoInfo {
  const char *opname;
  const char *gizmo;
  uint icon;
};

static struct NavigateGizmoInfo g_navigate_param = {
   .opname = "VIEW3D_OT_rotate",
   .gizmo = "VIEW3D_GT_navigate_rotate",
   .icon = ICON_NONE,
};

struct NavigateWidgetGroup {
  wmGizmo *gz_rotate;
  /* Store the view state to check for changes. */
  struct {
    rcti rect_visible;
    struct {
      char is_persp;
      bool is_camera;
      char viewlock;
    } rv3d;
  } state;
  int region_size[2];
};

static bool WIDGETGROUP_navigate_poll(const bContext *C, wmGizmoGroupType *UNUSED(gzgt))
{
  View3D *v3d = CTX_wm_view3d(C);
  if ((((U.uiflag & USER_SHOW_GIZMO_NAVIGATE) == 0) &&
       (U.mini_axis_type != USER_MINI_AXIS_TYPE_GIZMO)) ||
      (v3d->gizmo_flag & (V3D_GIZMO_HIDE | V3D_GIZMO_HIDE_NAVIGATE))) {
    return false;
  }
  return true;
}

static void WIDGETGROUP_navigate_setup(const bContext *C, wmGizmoGroup *gzgroup)
{
  struct NavigateWidgetGroup *navgroup = MEM_callocN(sizeof(struct NavigateWidgetGroup), __func__);

  navgroup->region_size[0] = -1;
  navgroup->region_size[1] = -1;

  wmOperatorType *ot_view_axis = WM_operatortype_find("VIEW3D_OT_view_axis", true);

  const struct NavigateGizmoInfo *info = &g_navigate_param;
  navgroup->gz_rotate =WM_gizmo_new(info->gizmo, gzgroup, NULL);
  wmGizmo *gz = navgroup->gz_rotate;
  gz->flag |= WM_GIZMO_MOVE_CURSOR | WM_GIZMO_DRAW_MODAL;
  
  gz->color[3] = 0.0f;
  copy_v3_fl(gz->color_hi, 0.5f);
  gz->color_hi[3] = 0.5f;
  
  /* may be overwritten later */
  gz->scale_basis = GIZMO_MINI_SIZE / 2.0f;
  if (info->icon != ICON_NONE) {
    PropertyRNA *prop = RNA_struct_find_property(gz->ptr, "icon");
    RNA_property_enum_set(gz->ptr, prop, info->icon);
    RNA_enum_set(
        gz->ptr, "draw_options", ED_GIZMO_BUTTON_SHOW_OUTLINE | ED_GIZMO_BUTTON_SHOW_BACKDROP);
  }

  wmOperatorType *ot = WM_operatortype_find(info->opname, true);
  WM_gizmo_operator_set(gz, 0, ot, NULL);
  
  /* Modal operators, don't use initial mouse location since we're clicking on a button. */
  {
    wmGizmoOpElem *gzop = WM_gizmo_operator_get(gz, 0);
    RNA_boolean_set(&gzop->ptr, "use_cursor_init", false);
  }

  {
    gz->scale_basis = GIZMO_SIZE / 2.0f;
    const char mapping[6] = {
        RV3D_VIEW_LEFT,
        RV3D_VIEW_RIGHT,
        RV3D_VIEW_FRONT,
        RV3D_VIEW_BACK,
        RV3D_VIEW_BOTTOM,
        RV3D_VIEW_TOP,
    };

    for (int part_index = 0; part_index < 6; part_index += 1) {
      PointerRNA *ptr = WM_gizmo_operator_set(gz, part_index + 1, ot_view_axis, NULL);
      RNA_enum_set(ptr, "type", mapping[part_index]);
    }

    /* When dragging an axis, use this instead. */
    wmWindowManager *wm = CTX_wm_manager(C);
    gz->keymap = WM_gizmo_keymap_generic_click_drag(wm);
    gz->drag_part = 0;
  }
    
  gzgroup->customdata = navgroup;
}

static void WIDGETGROUP_navigate_draw_prepare(const bContext *C, wmGizmoGroup *gzgroup)
{
  struct NavigateWidgetGroup *navgroup = gzgroup->customdata;
  ARegion *region = CTX_wm_region(C);
  const RegionView3D *rv3d = region->regiondata;

  for (int i = 0; i < 3; i++) {
    copy_v3_v3(navgroup->gz_rotate->matrix_offset[i], rv3d->viewmat[i]);
  }

  const rcti *rect_visible = ED_region_visible_rect(region);

  /* Ensure types match so bits are never lost on assignment. */
  CHECK_TYPE_PAIR(navgroup->state.rv3d.viewlock, rv3d->viewlock);

  if ((navgroup->state.rect_visible.xmax == rect_visible->xmax) &&
      (navgroup->state.rect_visible.ymax == rect_visible->ymax) &&
      (navgroup->state.rv3d.is_persp == rv3d->is_persp) &&
      (navgroup->state.rv3d.is_camera == (rv3d->persp == RV3D_CAMOB)) &&
      (navgroup->state.rv3d.viewlock == RV3D_LOCK_FLAGS(rv3d))) {
    return;
  }

  navgroup->state.rect_visible = *rect_visible;
  navgroup->state.rv3d.is_persp = rv3d->is_persp;
  navgroup->state.rv3d.is_camera = (rv3d->persp == RV3D_CAMOB);
  navgroup->state.rv3d.viewlock = RV3D_LOCK_FLAGS(rv3d);

  const bool show_rotate_gizmo = (U.mini_axis_type == USER_MINI_AXIS_TYPE_GIZMO);
  const float icon_offset = ((GIZMO_SIZE / 2.0f) + GIZMO_OFFSET) * UI_DPI_FAC;
  const float icon_offset_mini = (GIZMO_MINI_SIZE + GIZMO_MINI_OFFSET) * UI_DPI_FAC;
  const float co_rotate[2] = {
      rect_visible->xmin + icon_offset,
      rect_visible->ymin + icon_offset,
  };

  float icon_offset_from_axis = 0.0f;
  switch ((eUserpref_MiniAxisType)U.mini_axis_type) {
    case USER_MINI_AXIS_TYPE_GIZMO:
      icon_offset_from_axis = icon_offset * 2.1f;
      break;
    case USER_MINI_AXIS_TYPE_MINIMAL:
      icon_offset_from_axis = (UI_UNIT_X * 2.5) + (U.rvisize * U.pixelsize * 2.0f);
      break;
    case USER_MINI_AXIS_TYPE_NONE:
      icon_offset_from_axis = icon_offset_mini * 0.75f;
      break;
  }

  wmGizmo *gz;

  gz = navgroup->gz_rotate;
  WM_gizmo_set_flag(gz, WM_GIZMO_HIDDEN, true);

  if (show_rotate_gizmo) {
    
    gz->matrix_basis[3][0] = roundf(co_rotate[0]);
    gz->matrix_basis[3][1] = roundf(co_rotate[1]);
    WM_gizmo_set_flag(gz, WM_GIZMO_HIDDEN, false);
  }

  
}

void VIEW3D_GGT_navigate(wmGizmoGroupType *gzgt)
{
  gzgt->name = "View3D Navigate";
  gzgt->idname = "VIEW3D_GGT_navigate";

  gzgt->flag |= (WM_GIZMOGROUPTYPE_PERSISTENT | WM_GIZMOGROUPTYPE_SCALE |
                 WM_GIZMOGROUPTYPE_DRAW_MODAL_ALL);

  gzgt->poll = WIDGETGROUP_navigate_poll;
  gzgt->setup = WIDGETGROUP_navigate_setup;
  gzgt->draw_prepare = WIDGETGROUP_navigate_draw_prepare;
}

/** \} */
