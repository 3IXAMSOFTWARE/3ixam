/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

 /** \file
  * \ingroup spview3d
  */

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

/* Buttin gizmo minimum size in unscaled pixels. */
#define GIZMO_HEX_MIN_SIZE 20.0f

/* Buttin gizmo line widht. */
#define GIZMO_HEX_LINE_WIDHT 2.0f

/* Buttin gizmo offset in unscaled pixels. */
#define GIZMO_TRIANGLE_OFFSET 20.0f


enum {
    GZ_INDEX_MOVE,
    GZ_INDEX_MOVE2,
    GZ_INDEX_MOVE3,

    GZ_INDEX_TOTAL
};

struct NavigateGizmoInfo {
    const char* opname;
    const char* gizmo;
    const bool invert;
    uint icon;
};

static struct NavigateGizmoInfo g_view_menu_params[GZ_INDEX_TOTAL] = {
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_triangle",
        .invert = true,
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_triangle",
        .invert = false,
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_triangle",
        .invert = true,
        .icon = ICON_VIEW_CAMERA,
    },
};

struct NavigateWidgetGroup {
    wmGizmo* gz_array[GZ_INDEX_TOTAL];
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

static bool WIDGETGROUP_view_menu_poll(const bContext* C, wmGizmoGroupType* UNUSED(gzgt))
{
  return true;
}

static void WIDGETGROUP_view_menu_setup(const bContext* C, wmGizmoGroup* gzgroup)
{
    struct NavigateWidgetGroup* navgroup = MEM_callocN(sizeof(struct NavigateWidgetGroup), __func__);

    navgroup->region_size[0] = -1;
    navgroup->region_size[1] = -1;

    for (int i = 0; i < GZ_INDEX_TOTAL; i++) {
        const struct NavigateGizmoInfo* info = &g_view_menu_params[i];
        navgroup->gz_array[i] = WM_gizmo_new(info->gizmo, gzgroup, NULL);
        wmGizmo* gz = navgroup->gz_array[i];
        gz->flag |= WM_GIZMO_MOVE_CURSOR | WM_GIZMO_DRAW_MODAL;

        uchar icon_color[3];
        UI_GetThemeColor3ubv(TH_TEXT, icon_color);
        int color_tint, color_tint_hi;
      
        if (icon_color[0] > 128) {
            color_tint = -40;
            color_tint_hi = 60;
            gz->color[3] = 0.5f;
            gz->color_hi[3] = 0.5f;
        }
        else {
            color_tint = 60;
            color_tint_hi = 60;
            gz->color[3] = 0.5f;
            gz->color_hi[3] = 0.75f;
        }
        UI_GetThemeColorShade3fv(TH_HEADER, color_tint, gz->color);
        UI_GetThemeColorShade3fv(TH_HEADER, color_tint_hi, gz->color_hi);
        
        gz->line_width = GIZMO_HEX_LINE_WIDHT;

        if (info->icon != ICON_NONE) {
            PropertyRNA* prop = RNA_struct_find_property(gz->ptr, "icon");
            RNA_property_enum_set(gz->ptr, prop, info->icon);
            RNA_enum_set(
                gz->ptr, "draw_options", ED_GIZMO_BUTTON_SHOW_OUTLINE | ED_GIZMO_BUTTON_SHOW_BACKDROP);
        }

        RNA_boolean_set(gz->ptr, "invert", info->invert);
        wmOperatorType* ot = WM_operatortype_find(info->opname, true);
        WM_gizmo_operator_set(gz, 0, ot, NULL);
    }

    /* Modal operators, don't use initial mouse location since we're clicking on a button. */
    {
        for (int i = 0; i < GZ_INDEX_TOTAL; i++) {
            wmGizmo* gz = navgroup->gz_array[i];
            wmGizmoOpElem* gzop = WM_gizmo_operator_get(gz, 0);
            RNA_boolean_set(&gzop->ptr, "use_cursor_init", false);
        }
      
    }

    gzgroup->customdata = navgroup;
}

static void WIDGETGROUP_view_menu_draw_prepare(const bContext* C, wmGizmoGroup* gzgroup)
{
    struct NavigateWidgetGroup* navgroup = gzgroup->customdata;
    ARegion* region = CTX_wm_region(C);
    const RegionView3D* rv3d = region->regiondata;

    const rcti* rect_visible = &region->drawrct;

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

    const float button_size = 40.0f;
    const float button_offset_x = (button_size + GIZMO_TRIANGLE_OFFSET) * UI_DPI_FAC;
    const float screen_offest_x = (button_size + GIZMO_TRIANGLE_OFFSET) * UI_DPI_FAC;
    const float screen_offest_y = (button_size + GIZMO_TRIANGLE_OFFSET) * UI_DPI_FAC;

    const float co[2] = {
        roundf(rect_visible->xmax - screen_offest_x),
        roundf(screen_offest_y),
    };

    wmGizmo* gz;

    for (uint i = 0; i < ARRAY_SIZE(navgroup->gz_array); i++) {
        gz = navgroup->gz_array[i];
        WM_gizmo_set_flag(gz, WM_GIZMO_HIDDEN, true);
    }

    const float pos[GZ_INDEX_TOTAL][2] = {
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1])},
        {roundf(co[0] - button_offset_x * 1.0), roundf(co[1])},
        {roundf(co[0] - button_offset_x * 2.0), roundf(co[1])},
    };

    for(uint i = 0; i < GZ_INDEX_TOTAL; i++){
      gz = navgroup->gz_array[i];
      gz->scale_basis = button_size;
      gz->matrix_basis[3][0] = pos[i][0];
      gz->matrix_basis[3][1] = pos[i][1];
      WM_gizmo_set_flag(gz, WM_GIZMO_HIDDEN, false);
    }
}

void VIEW3D_GGT_view_menu(wmGizmoGroupType* gzgt)
{
    gzgt->name = "View3D View Menu";
    gzgt->idname = "VIEW3D_GGT_view_menu";

    gzgt->flag |= (WM_GIZMOGROUPTYPE_PERSISTENT | WM_GIZMOGROUPTYPE_SCALE |
        WM_GIZMOGROUPTYPE_DRAW_MODAL_ALL);

    gzgt->poll = WIDGETGROUP_view_menu_poll;
    gzgt->setup = WIDGETGROUP_view_menu_setup;
    gzgt->draw_prepare = WIDGETGROUP_view_menu_draw_prepare;
}

/** \} */
