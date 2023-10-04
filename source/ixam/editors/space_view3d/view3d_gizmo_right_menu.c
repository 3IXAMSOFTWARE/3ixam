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
#define GIZMO_HEX_OFFSET 4.0f

enum {
    GZ_INDEX_SELECT,
    GZ_INDEX_LIST,
    GZ_INDEX_CURSOR,
    GZ_INDEX_2D,
    GZ_INDEX_CUBE,
    GZ_INDEX_SPHERE,
    GZ_INDEX_SHAPE1,
    GZ_INDEX_SHAPE2,
    GZ_INDEX_SHAPE3,
    GZ_INDEX_SHAPE4,
    GZ_INDEX_SHAPE5,
    GZ_INDEX_SHAPE6,
    GZ_INDEX_LIGHT,
    GZ_INDEX_MATERIAL,
    GZ_INDEX_CAMERA,
    GZ_INDEX_RULER,
    GZ_INDEX_MODIFIERS,
    GZ_INDEX_PARAMETERS,
    GZ_INDEX_STAR,
    GZ_INDEX_MOVE,
    GZ_INDEX_ROTATE,
    GZ_INDEX_SCALE,
    GZ_INDEX_FIND,

    GZ_INDEX_TOTAL
};

struct NavigateGizmoInfo {
    const char* opname;
    const char* gizmo;
    uint icon;
};

static struct NavigateGizmoInfo g_right_menu_params[GZ_INDEX_TOTAL] = {
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d",
        //.icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
        .icon = ICON_VIEW_CAMERA,
    },
    {
        .opname = "VIEW3D_OT_move",
        .gizmo = "GIZMO_GT_button_2d_hex",
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

static bool WIDGETGROUP_right_menu_poll(const bContext* C, wmGizmoGroupType* UNUSED(gzgt))
{
  return true;
}

static const uchar shape_plus[] = {
    0x73, 0x73, 0x73, 0x36, 0x8c, 0x36, 0x8c, 0x73, 0xc9, 0x73, 0xc9, 0x8c, 0x8c,
    0x8c, 0x8c, 0xc9, 0x73, 0xc9, 0x73, 0x8c, 0x36, 0x8c, 0x36, 0x73, 0x36, 0x73,
};

static void WIDGETGROUP_right_menu_setup(const bContext* C, wmGizmoGroup* gzgroup)
{
    struct NavigateWidgetGroup* navgroup = MEM_callocN(sizeof(struct NavigateWidgetGroup), __func__);

    navgroup->region_size[0] = -1;
    navgroup->region_size[1] = -1;

    for (int i = 0; i < GZ_INDEX_TOTAL; i++) {
        const struct NavigateGizmoInfo* info = &g_right_menu_params[i];
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
        if(i == GZ_INDEX_SELECT)
        {
            PropertyRNA *prop = RNA_struct_find_property(gz->ptr, "shape");
            RNA_property_string_set_bytes(gz->ptr, prop, (const char *)shape_plus, ARRAY_SIZE(shape_plus));
        }

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

static void WIDGETGROUP_right_menu_draw_prepare(const bContext* C, wmGizmoGroup* gzgroup)
{
    struct NavigateWidgetGroup* navgroup = gzgroup->customdata;
    ARegion* region = CTX_wm_region(C);
    const RegionView3D* rv3d = region->regiondata;

    const rcti* rect_visible = ED_region_visible_rect(region);

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

    const float button_size = max_ff(rect_visible->ymax / 26.0f * 1.1f, GIZMO_HEX_MIN_SIZE);
    const float button_offset_y = (3.0f * button_size / 2.0f + GIZMO_HEX_OFFSET) * UI_DPI_FAC;
    const float button_offset_x = (sqrtf(3.0f) * button_size + GIZMO_HEX_OFFSET) * UI_DPI_FAC;
    const float screen_offest_x = (sqrtf(3.0f) * button_size / 2.0f + GIZMO_HEX_OFFSET) * UI_DPI_FAC;
    const float screen_offest_y = (3.0f * button_size / 4.0f * 1.4f + GIZMO_HEX_OFFSET) * UI_DPI_FAC;

    const float co[2] = {
        roundf(rect_visible->xmax - screen_offest_x),
        roundf(rect_visible->ymax - screen_offest_y),
    };

    wmGizmo* gz;

    for (uint i = 0; i < ARRAY_SIZE(navgroup->gz_array); i++) {
        gz = navgroup->gz_array[i];
        WM_gizmo_set_flag(gz, WM_GIZMO_HIDDEN, true);
    }

    const float pos[GZ_INDEX_TOTAL][2] = {
        {roundf(co[0] - button_offset_x * 2.0), roundf(co[1] - button_offset_y * 0.0)},
        {roundf(co[0] - button_offset_x * 1.0), roundf(co[1] - button_offset_y * 0.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 0.0)},
      
        {roundf(co[0] - button_offset_x * 1.5), roundf(co[1] - button_offset_y * 1.0)},
        {roundf(co[0] - button_offset_x * 0.5), roundf(co[1] - button_offset_y * 1.0)},
      
        {roundf(co[0] - button_offset_x * 1.0), roundf(co[1] - button_offset_y * 2.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 2.0)},
      
        {roundf(co[0] - button_offset_x * 0.5), roundf(co[1] - button_offset_y * 3.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 4.0)},
        {roundf(co[0] - button_offset_x * 0.5), roundf(co[1] - button_offset_y * 5.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 6.0)},
        {roundf(co[0] - button_offset_x * 0.5), roundf(co[1] - button_offset_y * 7.0)},
      
        {roundf(co[0] - button_offset_x * 1.0), roundf(co[1] - button_offset_y * 8.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 8.0)},
      
        {roundf(co[0] - button_offset_x * 0.5), roundf(co[1] - button_offset_y * 9.0)},
      
        {roundf(co[0] - button_offset_x * 1.0), roundf(co[1] - button_offset_y * 10.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 10.0)},
      
        {roundf(co[0] - button_offset_x * 1.5), roundf(co[1] - button_offset_y * 11.0)},
        {roundf(co[0] - button_offset_x * 0.5), roundf(co[1] - button_offset_y * 11.0)},
      
        {roundf(co[0] - button_offset_x * 3.0), roundf(co[1] - button_offset_y * 12.0)},
        {roundf(co[0] - button_offset_x * 2.0), roundf(co[1] - button_offset_y * 12.0)},
        {roundf(co[0] - button_offset_x * 1.0), roundf(co[1] - button_offset_y * 12.0)},
        {roundf(co[0] - button_offset_x * 0.0), roundf(co[1] - button_offset_y * 12.0)},
    };

    for(uint i = 0; i < GZ_INDEX_TOTAL; i++){
      gz = navgroup->gz_array[i];
      gz->scale_basis = button_size;
      gz->matrix_basis[3][0] = pos[i][0];
      gz->matrix_basis[3][1] = pos[i][1];
      WM_gizmo_set_flag(gz, WM_GIZMO_HIDDEN, false);
    }
}

void VIEW3D_GGT_right_menu(wmGizmoGroupType* gzgt)
{
    gzgt->name = "View3D Right Menu";
    gzgt->idname = "VIEW3D_GGT_right_menu";

    gzgt->flag |= (WM_GIZMOGROUPTYPE_PERSISTENT | WM_GIZMOGROUPTYPE_SCALE |
        WM_GIZMOGROUPTYPE_DRAW_MODAL_ALL);

    gzgt->poll = WIDGETGROUP_right_menu_poll;
    gzgt->setup = WIDGETGROUP_right_menu_setup;
    gzgt->draw_prepare = WIDGETGROUP_right_menu_draw_prepare;
}

/** \} */
