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
 * \ingroup edgizmolib
 *
 * \name Button Gizmo Hexß
 *
 * 2D Gizmo, also works in 3D views.
 *
 * \brief Single click button action for use in gizmo groups.
 *
 * \note Currently only basic icon & vector-shape buttons are supported.
 */

#include "MEM_guardedalloc.h"

#include "BLI_math.h"

#include "BKE_context.h"

#include "GPU_batch.h"
#include "GPU_batch_utils.h"
#include "GPU_immediate.h"
#include "GPU_immediate_util.h"
#include "GPU_matrix.h"
#include "GPU_select.h"
#include "GPU_state.h"

#include "RNA_access.h"
#include "RNA_define.h"
#include "RNA_enum_types.h"

#include "WM_api.h"
#include "WM_types.h"

#include "ED_gizmo_library.h"
#include "ED_screen.h"
#include "ED_view3d.h"

#include "UI_interface.h"
#include "UI_interface_icons.h"
#include "UI_resources.h"

/* own includes */
#include "../gizmo_geometry.h"
#include "../gizmo_library_intern.h"

/* -------------------------------------------------------------------- */
/** \name Internal Types
 * \{ */

typedef struct ButtonGizmo2DHex {
  wmGizmo gizmo;
  bool is_init;
  /* Use an icon or shape */
  int icon;
  GPUBatch *shape_batch[2];
} ButtonGizmo2DHex;

#define CIRCLE_RESOLUTION 6

/** \} */

/* -------------------------------------------------------------------- */
/** \name Internal API
 * \{ */

static void imm_draw_hexagon(uint shdr_pos, GPUPrimType type)
{
  immBegin(type, 6);
  for (int i = 0; i < 6; i++) {
    const float angle = (float)(2 * M_PI) * ((float)i / (float)6);
    immVertex2f(shdr_pos, (1.0f * sinf(angle)), (1.0f * cosf(angle)));
  }
  immEnd();
}

static void button2d_hex_geom_draw_backdrop(const wmGizmo *gz,
                                        const float color[4],
                                        const float fill_alpha,
                                        const bool select)
{
  float viewport[4];
  GPU_viewport_size_get_f(viewport);

  GPUVertFormat *format = immVertexFormat();
  uint pos = GPU_vertformat_attr_add(format, "pos", GPU_COMP_F32, 2, GPU_FETCH_FLOAT);

  /*
  const float fill_color[4] = {UNPACK3(color), fill_alpha * color[3]};
  immBindBuiltinProgram(GPU_SHADER_3D_UNIFORM_COLOR);
  immUniformColor4fv(fill_color);
  imm_draw_hexagon(pos, GPU_PRIM_TRI_FAN);
  immUnbindProgram();
  */

  immBindBuiltinProgram(GPU_SHADER_3D_POLYLINE_UNIFORM_COLOR);
  immUniform2fv("viewportSize", &viewport[2]);
  immUniform1f("lineWidth", gz->line_width * U.pixelsize);
  immUniformColor4fv(color);
  imm_draw_hexagon(pos, GPU_PRIM_LINE_LOOP);
  immUnbindProgram();

  UNUSED_VARS(select);
}

static void button2d_hex_draw_intern(const bContext *C,
                                 wmGizmo *gz,
                                 const bool select,
                                 const bool highlight)
{
  ButtonGizmo2DHex *button = (ButtonGizmo2DHex *)gz;
  float viewport[4];
  GPU_viewport_size_get_f(viewport);

  const int draw_options = RNA_enum_get(gz->ptr, "draw_options");
  if (button->is_init == false) {
    button->is_init = true;
    PropertyRNA *prop = RNA_struct_find_property(gz->ptr, "icon");
    button->icon = RNA_property_enum_get(gz->ptr, prop);
  }

  float color[4];
  float matrix_final[4][4];

  gizmo_color_get(gz, highlight, color);
  WM_gizmo_calc_matrix_final(gz, matrix_final);

  bool need_to_pop = true;
  GPU_matrix_push();
  GPU_matrix_mul(matrix_final);

  if (select) {
    button2d_hex_geom_draw_backdrop(gz, color, 1.0, select);
  }
  else {

    GPU_blend(GPU_BLEND_ALPHA);

    if (draw_options & ED_GIZMO_BUTTON_SHOW_BACKDROP) {
      const float fill_alpha = RNA_float_get(gz->ptr, "backdrop_fill_alpha");
      button2d_hex_geom_draw_backdrop(gz, color, fill_alpha, select);
    }

    if (button->icon != -1) {
      float pos[2];
      
      const float fac = gz->scale_basis / 20.0f;

      pos[0] = 0.0;
      pos[1] = 0.0;
      GPU_matrix_translate_2f(-(fac / 4), -(fac / 4));
      GPU_matrix_scale_2f(fac / (32.0f * UI_DPI_FAC),
                          fac / (32.0f * UI_DPI_FAC));
      
      
      float alpha = (highlight) ? 1.0f : 0.8f;
      GPU_polygon_smooth(false);
      UI_icon_draw_alpha(pos[0], pos[1], button->icon, alpha);
      GPU_polygon_smooth(true);
    }
    GPU_blend(GPU_BLEND_NONE);
  }

  if (need_to_pop) {
    GPU_matrix_pop();
  }
}

static void gizmo_button2d_hex_draw_select(const bContext *C, wmGizmo *gz, int select_id)
{
  GPU_select_load_id(select_id);
  button2d_hex_draw_intern(C, gz, true, false);
}

static void gizmo_button2d_hex_draw(const bContext *C, wmGizmo *gz)
{
  const bool is_highlight = (gz->state & WM_GIZMO_STATE_HIGHLIGHT) != 0;

  GPU_blend(GPU_BLEND_ALPHA);
  button2d_hex_draw_intern(C, gz, false, is_highlight);
  GPU_blend(GPU_BLEND_NONE);
}

static int gizmo_button2d_hex_test_select(bContext *C, wmGizmo *gz, const int mval[2])
{
  float point_local[2];
  const float m = gz->scale_final * cosf(M_PI / 6);
      
  copy_v2_v2(point_local, (float[2]){UNPACK2(mval)});
  sub_v2_v2(point_local, gz->matrix_basis[3]);
  
  const float a = atan2f(point_local[0], point_local[1]);
  const float scale = (gz->scale_final + m) / 2.0f + cosf(a * 6.0f) * (gz->scale_final - m) / 2.0f;
    
  mul_v2_fl(point_local, 1.0f / scale);

  if (len_v2(point_local) < 1.0f) {
    return 0;
  }

  return -1;
}

static int gizmo_button2d_hex_cursor_get(wmGizmo *gz)
{
  return WM_CURSOR_DEFAULT;

  if (RNA_boolean_get(gz->ptr, "show_drag")) {
    return WM_CURSOR_NSEW_SCROLL;
  }
  return WM_CURSOR_DEFAULT;
}

static bool gizmo_button2d_hex_bounds(bContext *C, wmGizmo *gz, rcti *r_bounding_box)
{
  ScrArea *area = CTX_wm_area(C);
  float rad = CIRCLE_RESOLUTION * U.dpi_fac / 2.0f;
  const float *co = NULL;
  float matrix_final[4][4];
  float co_proj[3];
  WM_gizmo_calc_matrix_final(gz, matrix_final);

  if (gz->parent_gzgroup->type->flag & WM_GIZMOGROUPTYPE_3D) {
    ARegion *region = CTX_wm_region(C);
    if (ED_view3d_project_float_global(region, matrix_final[3], co_proj, V3D_PROJ_TEST_NOP) ==
        V3D_PROJ_RET_OK) {
      float matrix_final_no_offset[4][4];
      const RegionView3D *rv3d = region->regiondata;
      WM_gizmo_calc_matrix_final_no_offset(gz, matrix_final_no_offset);
      const float factor = ED_view3d_pixel_size_no_ui_scale(rv3d, matrix_final_no_offset[3]) /
                           ED_view3d_pixel_size_no_ui_scale(rv3d, matrix_final[3]);
      /* It's possible (although unlikely) `matrix_final_no_offset` is behind the view.
       * `matrix_final` has already been projected so both can't be negative. */
      if (factor > 0.0f) {
        rad *= factor;
      }
      co = co_proj;
    }
  }
  else {
    co = matrix_final[3];
  }

  if (co != NULL) {
    r_bounding_box->xmin = co[0] + area->totrct.xmin - rad;
    r_bounding_box->ymin = co[1] + area->totrct.ymin - rad;
    r_bounding_box->xmax = r_bounding_box->xmin + rad;
    r_bounding_box->ymax = r_bounding_box->ymin + rad;
    return true;
  }
  return false;
}

static void gizmo_button2d_hex_free(wmGizmo *gz)
{
  ButtonGizmo2DHex *shape = (ButtonGizmo2DHex *)gz;

  for (uint i = 0; i < ARRAY_SIZE(shape->shape_batch); i++) {
    GPU_BATCH_DISCARD_SAFE(shape->shape_batch[i]);
  }
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Button Gizmo API
 * \{ */

static void GIZMO_GT_button_2d_hex(wmGizmoType *gzt)
{
  /* identifiers */
  gzt->idname = "GIZMO_GT_button_2d_hex";

  /* api callbacks */
  gzt->draw = gizmo_button2d_hex_draw;
  gzt->draw_select = gizmo_button2d_hex_draw_select;
  gzt->test_select = gizmo_button2d_hex_test_select;
  gzt->cursor_get = gizmo_button2d_hex_cursor_get;
  gzt->screen_bounds_get = gizmo_button2d_hex_bounds;
  gzt->free = gizmo_button2d_hex_free;

  gzt->struct_size = sizeof(ButtonGizmo2DHex);

  /* rna */
  static EnumPropertyItem rna_enum_draw_options[] = {
      {ED_GIZMO_BUTTON_SHOW_OUTLINE, "OUTLINE", 0, "Outline", ""},
      {ED_GIZMO_BUTTON_SHOW_BACKDROP, "BACKDROP", 0, "Backdrop", ""},
      {ED_GIZMO_BUTTON_SHOW_HELPLINE, "HELPLINE", 0, "Help Line", ""},
      {0, NULL, 0, NULL, NULL},
  };
  PropertyRNA *prop;

  RNA_def_enum_flag(gzt->srna, "draw_options", rna_enum_draw_options, 0, "Draw Options", "");

  prop = RNA_def_property(gzt->srna, "icon", PROP_ENUM, PROP_NONE);
  RNA_def_property_enum_items(prop, rna_enum_icon_items);

  /* Currently only used for cursor display. */
  RNA_def_boolean(gzt->srna, "show_drag", true, "Show Drag", "");

  RNA_def_float(gzt->srna,
                "backdrop_fill_alpha",
                1.0f,
                0.0f,
                1.0,
                "When below 1.0, draw the interior with a reduced alpha compared to the outline",
                "",
                0.0f,
                1.0f);
}

void ED_gizmotypes_button_2d_hex(void)
{
  WM_gizmotype_append(GIZMO_GT_button_2d_hex);
}

/** \} */ /* Button Gizmo APIß */
