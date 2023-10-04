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
 *
 * The Original Code is Copyright (C) 2001-2002 by NaN Holding BV.
 * All rights reserved.
 */

/** \file
 * \ingroup spimage
 */

#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#ifndef WIN32
#  include <unistd.h>
#else
#  include <io.h>
#endif

#include "MEM_guardedalloc.h"

#include "BLI_ixamlib.h"
#include "BLI_fileops.h"
#include "BLI_ghash.h"
#include "BLI_math.h"
#include "BLI_string.h"
#include "BLI_utildefines.h"

#include "BLT_translation.h"

#include "DNA_camera_types.h"
#include "DNA_node_types.h"
#include "DNA_object_types.h"
#include "DNA_scene_types.h"
#include "DNA_screen_types.h"

#include "BKE_colortools.h"
#include "BKE_context.h"
#include "BKE_global.h"
#include "BKE_icons.h"
#include "BKE_image.h"
#include "BKE_image_save.h"
#include "BKE_image_format.h"
#include "BKE_layer.h"
#include "BKE_lib_id.h"
#include "BKE_main.h"
#include "BKE_packedFile.h"
#include "BKE_report.h"

#include "DEG_depsgraph.h"

#include "GPU_state.h"

#include "IMB_colormanagement.h"
#include "IMB_imbuf.h"
#include "IMB_imbuf_types.h"
#include "IMB_moviecache.h"

#include "RE_pipeline.h"

#include "RNA_access.h"
#include "RNA_define.h"
#include "RNA_enum_types.h"
#include "RNA_prototypes.h"

#include "ED_image.h"
#include "ED_mask.h"
#include "ED_paint.h"
#include "ED_render.h"
#include "ED_screen.h"
#include "ED_space_api.h"
#include "ED_util.h"
#include "ED_util_imbuf.h"
#include "ED_uvedit.h"

#include "UI_interface.h"
#include "UI_resources.h"
#include "UI_view2d.h"

#include "WM_api.h"
#include "WM_types.h"

#include "PIL_time.h"

#include "RE_engine.h"

#include "space_render_intern.h"


static Image *render_image_from_context(const bContext *C)
{
  /* Edit image is set by templates used throughout the interface, so image
   * operations work outside the image editor. */
  Image *ima = CTX_data_pointer_get_type(C, "edit_image", &RNA_Image).data;

  if (ima) {
    return ima;
  }

  /* Image editor. */
  SpaceRender *srender = CTX_wm_space_render(C);
  return (srender) ? srender->image : NULL;
}

static ImageUser *render_image_user_from_context(const bContext *C)
{
  /* Edit image user is set by templates used throughout the interface, so
   * image operations work outside the image editor. */
  ImageUser *iuser = CTX_data_pointer_get_type(C, "edit_image_user", &RNA_ImageUser).data;

  if (iuser) {
    return iuser;
  }

  /* Image editor. */
  SpaceRender *srender = CTX_wm_space_render(C);
  return (srender) ? &srender->iuser : NULL;
}

static bool remder_image_from_context_has_data_poll(bContext *C)
{
  Image *ima = render_image_from_context(C);
  ImageUser *iuser = render_image_user_from_context(C);

  if (ima == NULL) {
    return false;
  }

  void *lock;
  ImBuf *ibuf = BKE_image_acquire_ibuf(ima, iuser, &lock);
  if (!ibuf) {
    return false;
  }
  const bool has_buffer = (ibuf && (ibuf->rect || ibuf->rect_float));
  BKE_image_release_ibuf(ima, ibuf, lock);
  return has_buffer;
}

/**
 * Use this when the image buffer is accessed without the image user.
 */
static bool render_image_from_context_has_data_poll_no_image_user(bContext *C)
{
  Image *ima = render_image_from_context(C);

  return BKE_image_has_ibuf(ima, NULL);
}

static bool render_image_not_packed_poll(bContext *C)
{
  /* Do not run 'replace' on packed images, it does not give user expected results at all. */
  Image *ima = render_image_from_context(C);
  return (ima && BLI_listbase_is_empty(&ima->packedfiles));
}

bool space_render_main_region_poll(bContext *C)
{
  SpaceRender *srender = CTX_wm_space_render(C);
  /* XXX ARegion *region = CTX_wm_region(C); */

  if (srender) {
    return true; /* XXX (region && region->type->regionid == RGN_TYPE_WINDOW); */
  }
  return false;
}

/* For RENDER_OT_curves_point_set to avoid sampling when in uv smooth mode or editmode */
static bool space_render_main_area_not_uv_brush_poll(bContext *C)
{
  SpaceRender *srender = CTX_wm_space_render(C);
  Scene *scene = CTX_data_scene(C);
  ToolSettings *toolsettings = scene->toolsettings;

  if (srender && !toolsettings->uvsculpt && (CTX_data_edit_object(C) == NULL)) {
    return true;
  }

  return false;
}



/* -------------------------------------------------------------------- */
/** \name Save Image As Operator
 * \{ */

typedef struct RenderImageSaveData {
  ImageUser *iuser;
  Image *image;
  ImageFormatData im_format;
} RenderImageSaveData;

static char render_imtype_best_depth(ImBuf *ibuf, const char imtype)
{
  const char depth_ok = BKE_imtype_valid_depths(imtype);

  if (ibuf->rect_float) {
   if (depth_ok & R_IMF_CHAN_DEPTH_32) {
      return R_IMF_CHAN_DEPTH_32;
    }
    if (depth_ok & R_IMF_CHAN_DEPTH_24) {
      return R_IMF_CHAN_DEPTH_24;
    }
    if (depth_ok & R_IMF_CHAN_DEPTH_16) {
      return R_IMF_CHAN_DEPTH_16;
    }
    if (depth_ok & R_IMF_CHAN_DEPTH_12) {
      return R_IMF_CHAN_DEPTH_12;
    }
    return R_IMF_CHAN_DEPTH_8;
  }

  if (depth_ok & R_IMF_CHAN_DEPTH_8) {
    return R_IMF_CHAN_DEPTH_8;
  }
  if (depth_ok & R_IMF_CHAN_DEPTH_12) {
    return R_IMF_CHAN_DEPTH_12;
  }
  if (depth_ok & R_IMF_CHAN_DEPTH_16) {
    return R_IMF_CHAN_DEPTH_16;
  }
  if (depth_ok & R_IMF_CHAN_DEPTH_24) {
    return R_IMF_CHAN_DEPTH_24;
  }
  if (depth_ok & R_IMF_CHAN_DEPTH_32) {
    return R_IMF_CHAN_DEPTH_32;
  }
  return R_IMF_CHAN_DEPTH_8; /* fallback, should not get here */
}

static int render_image_save_options_init(Main *bmain,
                                   ImageSaveOptions *opts,
                                   Image *ima,
                                   ImageUser *iuser,
                                   const bool guess_path,
                                   const bool save_as_render)
{
  void *lock;
  ImBuf *ibuf = BKE_image_acquire_ibuf(ima, iuser, &lock);

  if (ibuf) {
    Scene *scene = opts->scene;
    bool is_depth_set = false;

    if (ELEM(ima->type, IMA_TYPE_R_RESULT, IMA_TYPE_COMPOSITE)) {
      /* imtype */
      opts->im_format = scene->r.im_format;
      is_depth_set = true;
      if (!BKE_image_is_multiview(ima)) {
        /* In case multiview is disabled,
         * render settings would be invalid for render result in this area. */
        opts->im_format.stereo3d_format = *ima->stereo3d_format;
        opts->im_format.views_format = ima->views_format;
      }
    }
    else {
      if (ima->source == IMA_SRC_GENERATED) {
        opts->im_format.imtype = R_IMF_IMTYPE_PNG;
        opts->im_format.compress = ibuf->foptions.quality;
        opts->im_format.planes = ibuf->planes;
      }

      /* use the multiview image settings as the default */
      opts->im_format.stereo3d_format = *ima->stereo3d_format;
      opts->im_format.views_format = ima->views_format;
    }

    if (ima->source == IMA_SRC_TILED) {
      BLI_strncpy(opts->filepath, ima->filepath, sizeof(opts->filepath));
      BLI_path_abs(opts->filepath, ID_IXAM_PATH_FROM_GLOBAL(&ima->id));
    }
    else {
      BLI_strncpy(opts->filepath, ibuf->name, sizeof(opts->filepath));
    }

    /* sanitize all settings */

    /* unlikely but just in case */
    if (ELEM(opts->im_format.planes, R_IMF_PLANES_BW, R_IMF_PLANES_RGB, R_IMF_PLANES_RGBA) == 0) {
      opts->im_format.planes = R_IMF_PLANES_RGBA;
    }

    /* depth, account for float buffer and format support */
    if (is_depth_set == false) {
      opts->im_format.depth = render_imtype_best_depth(ibuf, opts->im_format.imtype);
    }

    /* some formats don't use quality so fallback to scenes quality */
    if (opts->im_format.quality == 0) {
      opts->im_format.quality = scene->r.im_format.quality;
    }

    /* check for empty path */
    if (guess_path && opts->filepath[0] == 0) {
      const bool is_prev_save = !STREQ(G.ima, "//");
      if (save_as_render) {
        if (is_prev_save) {
          BLI_strncpy(opts->filepath, G.ima, sizeof(opts->filepath));
        }
        else {
          BLI_strncpy(opts->filepath, "//untitled", sizeof(opts->filepath));
          BLI_path_abs(opts->filepath, BKE_main_ixamfile_path(bmain));
        }
      }
      else {
        BLI_snprintf(opts->filepath, sizeof(opts->filepath), "//%s", ima->id.name + 2);
        BLI_path_make_safe(opts->filepath);
        BLI_path_abs(opts->filepath, is_prev_save ? G.ima : BKE_main_ixamfile_path(bmain));
      }

      /* append UDIM marker if not present */
      if (ima->source == IMA_SRC_TILED && strstr(opts->filepath, "<UDIM>") == NULL) {
        int len = strlen(opts->filepath);
        STR_CONCAT(opts->filepath, len, ".<UDIM>");
      }
    }

    /* color management */
    BKE_color_managed_display_settings_copy(&opts->im_format.display_settings,
                                            &scene->display_settings);

    BKE_color_managed_view_settings_free(&opts->im_format.view_settings);
    BKE_color_managed_view_settings_copy(&opts->im_format.view_settings, &scene->view_settings);
  }

  BKE_image_release_ibuf(ima, ibuf, lock);

  return (ibuf != NULL);
}

static void render_image_save_options_from_op(Main *bmain,
                                       ImageSaveOptions *opts,
                                       wmOperator *op,
                                       ImageFormatData *imf)
{
  if (imf) {
    BKE_color_managed_view_settings_free(&opts->im_format.view_settings);
    opts->im_format = *imf;
  }

  if (RNA_struct_property_is_set(op->ptr, "filepath")) {
    RNA_string_get(op->ptr, "filepath", opts->filepath);
    BLI_path_abs(opts->filepath, BKE_main_ixamfile_path(bmain));
  }
}

static void render_image_save_options_to_op(ImageSaveOptions *opts, wmOperator *op)
{
  if (op->customdata) {
    RenderImageSaveData *isd = op->customdata;
    BKE_color_managed_view_settings_free(&isd->im_format.view_settings);
    isd->im_format = opts->im_format;
  }

  RNA_string_set(op->ptr, "filepath", opts->filepath);
}

static bool save_render_image_op(
    Main *bmain, Image *ima, ImageUser *iuser, wmOperator *op, ImageSaveOptions *opts)
{
  opts->relative = (RNA_struct_find_property(op->ptr, "relative_path") &&
                    RNA_boolean_get(op->ptr, "relative_path"));
  opts->save_copy = (RNA_struct_find_property(op->ptr, "copy") &&
                     RNA_boolean_get(op->ptr, "copy"));
  opts->save_as_render = (RNA_struct_find_property(op->ptr, "save_as_render") &&
                          RNA_boolean_get(op->ptr, "save_as_render"));

  WM_cursor_wait(true);

  bool ok = BKE_image_save(op->reports, bmain, ima, iuser, opts);

  WM_cursor_wait(false);

  /* Remember file path for next save. */
  BLI_strncpy(G.ima, opts->filepath, sizeof(G.ima));

  WM_main_add_notifier(NC_IMAGE | NA_EDITED, ima);

  return ok;
}

static void render_image_save_as_free(wmOperator *op)
{
  if (op->customdata) {
    RenderImageSaveData *isd = op->customdata;
    BKE_color_managed_view_settings_free(&isd->im_format.view_settings);

    MEM_freeN(op->customdata);
    op->customdata = NULL;
  }
}

static int render_image_save_as_exec(bContext *C, wmOperator *op)
{
  Main *bmain = CTX_data_main(C);
  Scene *scene = CTX_data_scene(C);
  ImageSaveOptions opts;

  Image *image = NULL;
  ImageUser *iuser = NULL;
  ImageFormatData *imf = NULL;
  if (op->customdata) {
    RenderImageSaveData *isd = op->customdata;
    image = isd->image;
    iuser = isd->iuser;
    imf = &isd->im_format;
  }
  else {
    image = render_image_from_context(C);
    iuser = render_image_user_from_context(C);
  }

  BKE_image_save_options_init(&opts, bmain, scene, image, iuser, false, false);

  /* just in case to initialize values,
   * these should be set on invoke or by the caller. */
  render_image_save_options_init(bmain, &opts, image, iuser, false, false);

  render_image_save_options_from_op(bmain, &opts, op, imf);
  opts.do_newpath = true;

  save_render_image_op(bmain, image, iuser, op, &opts);

  if (opts.save_copy == false) {
    BKE_image_free_packedfiles(image);
  }

  render_image_save_as_free(op);

  return OPERATOR_FINISHED;
}

static bool redner_image_save_as_check(bContext *UNUSED(C), wmOperator *op)
{
  RenderImageSaveData *isd = op->customdata;
  return WM_operator_filesel_ensure_ext_imtype(op, &isd->im_format);
}

static void render_image_filesel(bContext *C, wmOperator *op, const char *path)
{
  RNA_string_set(op->ptr, "filepath", path);
  WM_event_add_fileselect(C, op);
}

static int render_image_save_as_invoke(bContext *C, wmOperator *op, const wmEvent *UNUSED(event))
{
  Main *bmain = CTX_data_main(C);
  Image *ima = render_image_from_context(C);
  ImageUser *iuser = render_image_user_from_context(C);
  Scene *scene = CTX_data_scene(C);
  ImageSaveOptions opts;
  PropertyRNA *prop;
  const bool save_as_render = (ima->source == IMA_SRC_VIEWER);

  if (RNA_struct_property_is_set(op->ptr, "filepath")) {
    return render_image_save_as_exec(C, op);
  }

  BKE_image_save_options_init(&opts, bmain, scene, ima, iuser, false, false);

  if (render_image_save_options_init(bmain, &opts, ima, iuser, true, save_as_render) == 0) {
    return OPERATOR_CANCELLED;
  }
  render_image_save_options_to_op(&opts, op);

  /* enable save_copy by default for render results */
  if (ELEM(ima->type, IMA_TYPE_R_RESULT, IMA_TYPE_COMPOSITE) &&
      !RNA_struct_property_is_set(op->ptr, "copy")) {
    RNA_boolean_set(op->ptr, "copy", true);
  }

  RNA_boolean_set(op->ptr, "save_as_render", save_as_render);

  RenderImageSaveData *isd = MEM_callocN(sizeof(*isd), __func__);
  isd->image = ima;
  isd->iuser = iuser;

  memcpy(&isd->im_format, &opts.im_format, sizeof(opts.im_format));
  op->customdata = isd;

  /* show multiview save options only if image has multiviews */
  prop = RNA_struct_find_property(op->ptr, "show_multiview");
  RNA_property_boolean_set(op->ptr, prop, BKE_image_is_multiview(ima));
  prop = RNA_struct_find_property(op->ptr, "use_multiview");
  RNA_property_boolean_set(op->ptr, prop, BKE_image_is_multiview(ima));

  render_image_filesel(C, op, opts.filepath);

  return OPERATOR_RUNNING_MODAL;
}

static void render_age_save_as_cancel(bContext *UNUSED(C), wmOperator *op)
{
  render_image_save_as_free(op);
}

static bool render_image_save_as_draw_check_prop(PointerRNA *ptr,
                                                 PropertyRNA *prop,
                                                 void *UNUSED(user_data))
{
  const char *prop_id = RNA_property_identifier(prop);

  return !(STREQ(prop_id, "filepath") || STREQ(prop_id, "directory") ||
           STREQ(prop_id, "filename") ||
           /* when saving a copy, relative path has no effect */
           (STREQ(prop_id, "relative_path") && RNA_boolean_get(ptr, "copy")));
}

static void render_image_save_as_draw(bContext *UNUSED(C), wmOperator *op)
{
  uiLayout *layout = op->layout;
  RenderImageSaveData *isd = op->customdata;
  PointerRNA imf_ptr;
  const bool is_multiview = RNA_boolean_get(op->ptr, "show_multiview");

  /* image template */
  RNA_pointer_create(NULL, &RNA_ImageFormatSettings, &isd->im_format, &imf_ptr);
  uiTemplateImageSettings(layout, &imf_ptr, false);

  /* main draw call */
  uiDefAutoButsRNA(
      layout, op->ptr, render_image_save_as_draw_check_prop, NULL, NULL, UI_BUT_LABEL_ALIGN_NONE, false);

  /* multiview template */
  if (is_multiview) {
    uiTemplateImageFormatViews(layout, &imf_ptr, op->ptr);
  }
}

static bool render_image_save_as_poll(bContext *C)
{
  if (!remder_image_from_context_has_data_poll(C)) {
    return false;
  }

  if (G.is_rendering) {
    /* no need to NULL check here */
    Image *ima = render_image_from_context(C);

    if (ima->source == IMA_SRC_VIEWER) {
      CTX_wm_operator_poll_msg_set(C, "can't save image while rendering");
      return false;
    }
  }

  return true;
}

static void render_image_operator_prop_allow_tokens(wmOperatorType *ot)
{
  PropertyRNA *prop = RNA_def_boolean(
      ot->srna, "allow_path_tokens", true, "", "Allow the path to contain substitution tokens");
  RNA_def_property_flag(prop, PROP_HIDDEN);
}

void RENDER_OT_save_as(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Save As Image";
  ot->idname = "RENDER_OT_save_as";
  ot->description = "Save the image with another name and/or settings";

  /* api callbacks */
  ot->exec = render_image_save_as_exec;
  ot->check = redner_image_save_as_check;
  ot->invoke = render_image_save_as_invoke;
  ot->cancel = render_age_save_as_cancel;
  ot->ui = render_image_save_as_draw;
  ot->poll = render_image_save_as_poll;

  /* flags */
  ot->flag = OPTYPE_REGISTER | OPTYPE_UNDO;

  /* properties */
  RNA_def_boolean(ot->srna,
                  "save_as_render",
                  0,
                  "Save As Render",
                  "Apply render part of display transform when saving byte image");
  RNA_def_boolean(ot->srna,
                  "copy",
                  0,
                  "Copy",
                  "Create a new image file without modifying the current image in 3IXAM");

  render_image_operator_prop_allow_tokens(ot);
  WM_operator_properties_filesel(ot,
                                 FILE_TYPE_FOLDER | FILE_TYPE_IMAGE | FILE_TYPE_MOVIE,
                                 FILE_SPECIAL,
                                 FILE_SAVE,
                                 WM_FILESEL_FILEPATH | WM_FILESEL_RELPATH | WM_FILESEL_SHOW_PROPS,
                                 FILE_DEFAULTDISPLAY,
                                 FILE_SORT_DEFAULT);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Save Image Operator
 * \{ */

/**
 * \param iuser: Image user or NULL when called outside the image space.
 */
static bool render_image_file_format_writable(Image *ima, ImageUser *iuser)
{
  void *lock;
  ImBuf *ibuf = BKE_image_acquire_ibuf(ima, iuser, &lock);
  bool ret = false;

  if (ibuf && BKE_image_buffer_format_writable(ibuf)) {
    ret = true;
  }

  BKE_image_release_ibuf(ima, ibuf, lock);
  return ret;
}

static bool render_image_save_poll(bContext *C)
{
  /* Can't save if there are no pixels. */
  if (remder_image_from_context_has_data_poll(C) == false) {
    return false;
  }

  /* Check if there is a valid file path and image format we can write
   * outside of the 'poll' so we can show a report with a pop-up. */

  /* Can always repack images.
   * Images without a filepath will go to "Save As". */
  return true;
}

static int render_image_save_exec(bContext *C, wmOperator *op)
{
  Main *bmain = CTX_data_main(C);
  Image *image = render_image_from_context(C);
  ImageUser *iuser = render_image_user_from_context(C);
  Scene *scene = CTX_data_scene(C);
  ImageSaveOptions opts;
  bool ok = false;

  if (BKE_image_has_packedfile(image)) {
    /* Save packed files to memory. */
    BKE_image_memorypack(image);
    /* Report since this can be called from key shortcuts. */
    BKE_reportf(op->reports, RPT_INFO, "Packed to memory image \"%s\"", image->filepath);
    return OPERATOR_FINISHED;
  }

  BKE_image_save_options_init(&opts, bmain, scene, image, iuser, false, false);
  if (render_image_save_options_init(bmain, &opts, image, iuser, false, false) == 0) {
    return OPERATOR_CANCELLED;
  }
  render_image_save_options_from_op(bmain, &opts, op, NULL);

  /* Check if file write permission is ok. */
  if (BLI_exists(opts.filepath) && !BLI_file_is_writable(opts.filepath)) {
    BKE_reportf(
        op->reports, RPT_ERROR, "Cannot save image, path \"%s\" is not writable", opts.filepath);
  }
  else if (save_render_image_op(bmain, image, iuser, op, &opts)) {
    /* Report since this can be called from key shortcuts. */
    BKE_reportf(op->reports, RPT_INFO, "Saved image \"%s\"", opts.filepath);
    ok = true;
  }

  BKE_color_managed_view_settings_free(&opts.im_format.view_settings);

  if (ok) {
    return OPERATOR_FINISHED;
  }

  return OPERATOR_CANCELLED;
}

static int render_image_save_invoke(bContext *C, wmOperator *op, const wmEvent *UNUSED(event))
{
  Image *ima = render_image_from_context(C);
  ImageUser *iuser = render_image_user_from_context(C);

  /* Not writable formats or images without a file-path will go to "Save As". */
  if (!BKE_image_has_packedfile(ima) &&
      (!BKE_image_has_filepath(ima) || !render_image_file_format_writable(ima, iuser))) {
    WM_operator_name_call(C, "RENDER_OT_save_as", WM_OP_INVOKE_DEFAULT, NULL, NULL);
    return OPERATOR_CANCELLED;
  }
  return render_image_save_exec(C, op);
}

void RENDER_OT_save(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Save Image";
  ot->idname = "RENDER_OT_save";
  ot->description = "Save the image with current name and settings";

  /* api callbacks */
  ot->exec = render_image_save_exec;
  ot->invoke = render_image_save_invoke;
  ot->poll = render_image_save_poll;

  /* flags */
  ot->flag = OPTYPE_REGISTER | OPTYPE_UNDO;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Save Sequence Operator
 * \{ */

static int render_image_save_sequence_exec(bContext *C, wmOperator *op)
{
  Main *bmain = CTX_data_main(C);
  Image *image = render_image_from_context(C);
  ImBuf *ibuf, *first_ibuf = NULL;
  int tot = 0;
  char di[FILE_MAX];
  struct MovieCacheIter *iter;

  if (image == NULL) {
    return OPERATOR_CANCELLED;
  }

  if (image->source != IMA_SRC_SEQUENCE) {
    BKE_report(op->reports, RPT_ERROR, "Can only save sequence on image sequences");
    return OPERATOR_CANCELLED;
  }

  if (image->type == IMA_TYPE_MULTILAYER) {
    BKE_report(op->reports, RPT_ERROR, "Cannot save multilayer sequences");
    return OPERATOR_CANCELLED;
  }

  /* get total dirty buffers and first dirty buffer which is used for menu */
  ibuf = NULL;
  if (image->cache != NULL) {
    iter = IMB_moviecacheIter_new(image->cache);
    while (!IMB_moviecacheIter_done(iter)) {
      ibuf = IMB_moviecacheIter_getImBuf(iter);
      if (ibuf != NULL && ibuf->userflags & IB_BITMAPDIRTY) {
        if (first_ibuf == NULL) {
          first_ibuf = ibuf;
        }
        tot++;
      }
      IMB_moviecacheIter_step(iter);
    }
    IMB_moviecacheIter_free(iter);
  }

  if (tot == 0) {
    BKE_report(op->reports, RPT_WARNING, "No images have been changed");
    return OPERATOR_CANCELLED;
  }

  /* get a filename for menu */
  BLI_split_dir_part(first_ibuf->name, di, sizeof(di));
  BKE_reportf(op->reports, RPT_INFO, "%d image(s) will be saved in %s", tot, di);

  iter = IMB_moviecacheIter_new(image->cache);
  while (!IMB_moviecacheIter_done(iter)) {
    ibuf = IMB_moviecacheIter_getImBuf(iter);

    if (ibuf != NULL && ibuf->userflags & IB_BITMAPDIRTY) {
      char name[FILE_MAX];
      BLI_strncpy(name, ibuf->name, sizeof(name));

      BLI_path_abs(name, BKE_main_ixamfile_path(bmain));

      if (0 == IMB_saveiff(ibuf, name, IB_rect | IB_zbuf | IB_zbuffloat)) {
        BKE_reportf(op->reports, RPT_ERROR, "Could not write image: %s", strerror(errno));
        break;
      }

      BKE_reportf(op->reports, RPT_INFO, "Saved %s", ibuf->name);
      ibuf->userflags &= ~IB_BITMAPDIRTY;
    }

    IMB_moviecacheIter_step(iter);
  }
  IMB_moviecacheIter_free(iter);

  return OPERATOR_FINISHED;
}

void RENDER_OT_save_sequence(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Save Sequence";
  ot->idname = "RENDER_OT_save_sequence";
  ot->description = "Save a sequence of images";

  /* api callbacks */
  ot->exec = render_image_save_sequence_exec;
  ot->poll = remder_image_from_context_has_data_poll;

  /* flags */
  ot->flag = OPTYPE_REGISTER | OPTYPE_UNDO;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Save All Operator
 * \{ */

static bool render_image_should_be_saved_when_modified(Image *ima)
{
  return !ELEM(ima->type, IMA_TYPE_R_RESULT, IMA_TYPE_COMPOSITE);
}

static bool render_image_should_be_saved(Image *ima, bool *is_format_writable)
{
  if (BKE_image_is_dirty_writable(ima, is_format_writable) &&
      ELEM(ima->source, IMA_SRC_FILE, IMA_SRC_GENERATED, IMA_SRC_TILED)) {
    return render_image_should_be_saved_when_modified(ima);
  }
  return false;
}

static bool render_image_has_valid_path(Image *ima)
{
  return strchr(ima->filepath, '\\') || strchr(ima->filepath, '/');
}


static bool render_image_save_all_modified_poll(bContext *C)
{
  int num_files = ED_image_save_all_modified_info(CTX_data_main(C), NULL);
  return num_files > 0;
}

static int render_image_save_all_modified_exec(bContext *C, wmOperator *op)
{
  ED_image_save_all_modified(C, op->reports);
  return OPERATOR_FINISHED;
}

void RENDER_OT_save_all_modified(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Save All Modified";
  ot->idname = "RENDER_OT_save_all_modified";
  ot->description = "Save all modified images";

  /* api callbacks */
  ot->exec = render_image_save_all_modified_exec;
  ot->poll = render_image_save_all_modified_poll;

  /* flags */
  ot->flag = OPTYPE_REGISTER | OPTYPE_UNDO;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Reload Image Operator
 * \{ */

static int render_image_reload_exec(bContext *C, wmOperator *UNUSED(op))
{
  Main *bmain = CTX_data_main(C);
  Image *ima = render_image_from_context(C);
  ImageUser *iuser = render_image_user_from_context(C);

  if (!ima) {
    return OPERATOR_CANCELLED;
  }

  /* XXX BKE_packedfile_unpack_image frees image buffers */
  ED_preview_kill_jobs(CTX_wm_manager(C), CTX_data_main(C));

  BKE_image_signal(bmain, ima, iuser, IMA_SIGNAL_RELOAD);
  DEG_id_tag_update(&ima->id, 0);

  WM_event_add_notifier(C, NC_IMAGE | NA_EDITED, ima);

  return OPERATOR_FINISHED;
}

void RENDER_OT_reload(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Reload Image";
  ot->idname = "RENDER_OT_reload";
  ot->description = "Reload current image from disk";

  /* api callbacks */
  ot->exec = render_image_reload_exec;

  /* flags */
  ot->flag = OPTYPE_REGISTER; /* no undo, image buffer is not handled by undo */
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name New Image Operator
 * \{ */

#define IMA_DEF_NAME N_("Untitled")

enum {
  GEN_CONTEXT_NONE = 0,
  GEN_CONTEXT_PAINT_CANVAS = 1,
  GEN_CONTEXT_PAINT_STENCIL = 2,
};

typedef struct RenderImageNewData {
  PropertyPointerRNA pprop;
} RenderImageNewData;

static RenderImageNewData *render_image_new_init(bContext *C, wmOperator *op)
{
  if (op->customdata) {
    return op->customdata;
  }

  RenderImageNewData *data = MEM_callocN(sizeof(RenderImageNewData), __func__);
  UI_context_active_but_prop_get_templateID(C, &data->pprop.ptr, &data->pprop.prop);
  op->customdata = data;
  return data;
}

static void image_new_free(wmOperator *op)
{
  MEM_SAFE_FREE(op->customdata);
}

static int render_image_new_exec(bContext *C, wmOperator *op)
{
  SpaceRender *srender;
  Image *ima;
  Main *bmain;
  PropertyRNA *prop;
  char name_buffer[MAX_ID_NAME - 2];
  const char *name;
  float color[4];
  int width, height, floatbuf, gen_type, alpha;
  int stereo3d;

  /* retrieve state */
  srender = CTX_wm_space_render(C);
  bmain = CTX_data_main(C);

  prop = RNA_struct_find_property(op->ptr, "name");
  RNA_property_string_get(op->ptr, prop, name_buffer);
  if (!RNA_property_is_set(op->ptr, prop)) {
    /* Default value, we can translate! */
    name = DATA_(name_buffer);
  }
  else {
    name = name_buffer;
  }
  width = RNA_int_get(op->ptr, "width");
  height = RNA_int_get(op->ptr, "height");
  floatbuf = RNA_boolean_get(op->ptr, "float");
  gen_type = RNA_enum_get(op->ptr, "generated_type");
  RNA_float_get_array(op->ptr, "color", color);
  alpha = RNA_boolean_get(op->ptr, "alpha");
  stereo3d = RNA_boolean_get(op->ptr, "use_stereo_3d");
  bool tiled = RNA_boolean_get(op->ptr, "tiled");

  if (!alpha) {
    color[3] = 1.0f;
  }

  ima = BKE_image_add_generated(bmain,
                                width,
                                height,
                                name,
                                alpha ? 32 : 24,
                                floatbuf,
                                gen_type,
                                color,
                                stereo3d,
                                false,
                                tiled);

  if (!ima) {
    image_new_free(op);
    return OPERATOR_CANCELLED;
  }

  /* hook into UI */
  RenderImageNewData *data = render_image_new_init(C, op);

  if (data->pprop.prop) {
    /* when creating new ID blocks, use is already 1, but RNA
     * pointer use also increases user, so this compensates it */
    id_us_min(&ima->id);

    PointerRNA imaptr;
    RNA_id_pointer_create(&ima->id, &imaptr);
    RNA_property_pointer_set(&data->pprop.ptr, data->pprop.prop, imaptr, NULL);
    RNA_property_update(C, &data->pprop.ptr, data->pprop.prop);
  }
  else if (srender) {
    ED_space_image_set(bmain, (SpaceImage *)srender, ima, false);
  }
  else {
    /* #BKE_image_add_generated creates one user by default, remove it if image is not linked to
     * anything. ref. T94599. */
    id_us_min(&ima->id);
  }

  BKE_image_signal(bmain, ima, (srender) ? &srender->iuser : NULL, IMA_SIGNAL_USER_NEW_IMAGE);

  WM_event_add_notifier(C, NC_IMAGE | NA_ADDED, ima);

  image_new_free(op);

  return OPERATOR_FINISHED;
}

static int render_image_new_invoke(bContext *C, wmOperator *op, const wmEvent *UNUSED(event))
{
  /* Get property in advance, it doesn't work after WM_operator_props_dialog_popup. */
  RenderImageNewData *data;
  op->customdata = data = MEM_callocN(sizeof(RenderImageNewData), __func__);
  UI_context_active_but_prop_get_templateID(C, &data->pprop.ptr, &data->pprop.prop);

  /* Better for user feedback. */
  RNA_string_set(op->ptr, "name", DATA_(IMA_DEF_NAME));
  return WM_operator_props_dialog_popup(C, op, 300);
}

static void render_image_new_draw(bContext *UNUSED(C), wmOperator *op)
{
  uiLayout *col;
  uiLayout *layout = op->layout;
#if 0
  Scene *scene = CTX_data_scene(C);
  const bool is_multiview = (scene->r.scemode & R_MULTIVIEW) != 0;
#endif

  /* copy of WM_operator_props_dialog_popup() layout */

  uiLayoutSetPropSep(layout, true);
  uiLayoutSetPropDecorate(layout, false);

  col = uiLayoutColumn(layout, false);
  uiItemR(col, op->ptr, "name", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "width", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "height", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "color", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "alpha", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "generated_type", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "float", 0, NULL, ICON_NONE);
  uiItemR(col, op->ptr, "tiled", 0, NULL, ICON_NONE);

#if 0
  if (is_multiview) {
    uiItemL(col[0], "", ICON_NONE);
    uiItemR(col[1], op->ptr, "use_stereo_3d", 0, NULL, ICON_NONE);
  }
#endif
}

static void render_image_new_cancel(bContext *UNUSED(C), wmOperator *op)
{
  image_new_free(op);
}

void RENDER_OT_new(wmOperatorType *ot)
{
  PropertyRNA *prop;
  static float default_color[4] = {0.0f, 0.0f, 0.0f, 1.0f};

  /* identifiers */
  ot->name = "New Image";
  ot->description = "Create a new image";
  ot->idname = "RENDER_OT_new";

  /* api callbacks */
  ot->exec = render_image_new_exec;
  ot->invoke = render_image_new_invoke;
  ot->ui = render_image_new_draw;
  ot->cancel = render_image_new_cancel;

  /* flags */
  ot->flag = OPTYPE_UNDO;

  /* properties */
  RNA_def_string(ot->srna, "name", IMA_DEF_NAME, MAX_ID_NAME - 2, "Name", "Image data-block name");
  prop = RNA_def_int(ot->srna, "width", 1024, 1, INT_MAX, "Width", "Image width", 1, 16384);
  RNA_def_property_subtype(prop, PROP_PIXEL);
  prop = RNA_def_int(ot->srna, "height", 1024, 1, INT_MAX, "Height", "Image height", 1, 16384);
  RNA_def_property_subtype(prop, PROP_PIXEL);
  prop = RNA_def_float_color(
      ot->srna, "color", 4, NULL, 0.0f, FLT_MAX, "Color", "Default fill color", 0.0f, 1.0f);
  RNA_def_property_subtype(prop, PROP_COLOR_GAMMA);
  RNA_def_property_float_array_default(prop, default_color);
  RNA_def_boolean(ot->srna, "alpha", 1, "Alpha", "Create an image with an alpha channel");
  RNA_def_enum(ot->srna,
               "generated_type",
               rna_enum_image_generated_type_items,
               IMA_GENTYPE_BLANK,
               "Generated Type",
               "Fill the image with a grid for UV map testing");
  RNA_def_boolean(
      ot->srna, "float", 0, "32-bit Float", "Create image with 32-bit floating-point bit depth");
  RNA_def_property_flag(prop, PROP_HIDDEN);
  prop = RNA_def_boolean(
      ot->srna, "use_stereo_3d", 0, "Stereo 3D", "Create an image with left and right views");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE | PROP_HIDDEN);
  prop = RNA_def_boolean(ot->srna, "tiled", 0, "Tiled", "Create a tiled image");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);
}

#undef IMA_DEF_NAME

/** \} */

/* -------------------------------------------------------------------- */
/** \name Flip Operator
 * \{ */

static int render_image_flip_exec(bContext *C, wmOperator *op)
{
  Image *ima = render_image_from_context(C);
  ImBuf *ibuf = BKE_image_acquire_ibuf(ima, NULL, NULL);
  SpaceImage *sima = CTX_wm_space_image(C);
  const bool is_paint = ((sima != NULL) && (sima->mode == SI_MODE_PAINT));

  if (ibuf == NULL) {
    /* TODO: this should actually never happen, but does for render-results -> cleanup. */
    return OPERATOR_CANCELLED;
  }

  const bool use_flip_x = RNA_boolean_get(op->ptr, "use_flip_x");
  const bool use_flip_y = RNA_boolean_get(op->ptr, "use_flip_y");

  if (!use_flip_x && !use_flip_y) {
    BKE_image_release_ibuf(ima, ibuf, NULL);
    return OPERATOR_FINISHED;
  }

  ED_image_undo_push_begin_with_image(op->type->name, ima, ibuf, &sima->iuser);

  if (is_paint) {
    ED_imapaint_clear_partial_redraw();
  }

  const int size_x = ibuf->x;
  const int size_y = ibuf->y;

  if (ibuf->rect_float) {
    float *float_pixels = (float *)ibuf->rect_float;

    float *orig_float_pixels = MEM_dupallocN(float_pixels);
    for (int x = 0; x < size_x; x++) {
      const int source_pixel_x = use_flip_x ? size_x - x - 1 : x;
      for (int y = 0; y < size_y; y++) {
        const int source_pixel_y = use_flip_y ? size_y - y - 1 : y;

        const float *source_pixel =
            &orig_float_pixels[4 * (source_pixel_x + source_pixel_y * size_x)];
        float *target_pixel = &float_pixels[4 * (x + y * size_x)];

        copy_v4_v4(target_pixel, source_pixel);
      }
    }
    MEM_freeN(orig_float_pixels);

    if (ibuf->rect) {
      IMB_rect_from_float(ibuf);
    }
  }
  else if (ibuf->rect) {
    char *char_pixels = (char *)ibuf->rect;
    char *orig_char_pixels = MEM_dupallocN(char_pixels);
    for (int x = 0; x < size_x; x++) {
      const int source_pixel_x = use_flip_x ? size_x - x - 1 : x;
      for (int y = 0; y < size_y; y++) {
        const int source_pixel_y = use_flip_y ? size_y - y - 1 : y;

        const char *source_pixel =
            &orig_char_pixels[4 * (source_pixel_x + source_pixel_y * size_x)];
        char *target_pixel = &char_pixels[4 * (x + y * size_x)];

        copy_v4_v4_char(target_pixel, source_pixel);
      }
    }
    MEM_freeN(orig_char_pixels);
  }
  else {
    BKE_image_release_ibuf(ima, ibuf, NULL);
    return OPERATOR_CANCELLED;
  }

  ibuf->userflags |= IB_DISPLAY_BUFFER_INVALID;
  BKE_image_mark_dirty(ima, ibuf);

  if (ibuf->mipmap[0]) {
    ibuf->userflags |= IB_MIPMAP_INVALID;
  }

  ED_image_undo_push_end();

  /* force GPU re-upload, all image is invalid. */
  BKE_image_free_gputextures(ima);

  WM_event_add_notifier(C, NC_IMAGE | NA_EDITED, ima);

  BKE_image_release_ibuf(ima, ibuf, NULL);

  return OPERATOR_FINISHED;
}

void RENDER_OT_flip(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Flip Image";
  ot->idname = "RENDER_OT_flip";
  ot->description = "Flip the image";

  /* api callbacks */
  ot->exec = render_image_flip_exec;
  ot->poll = render_image_from_context_has_data_poll_no_image_user;

  /* properties */
  PropertyRNA *prop;
  prop = RNA_def_boolean(
      ot->srna, "use_flip_x", false, "Horizontal", "Flip the image horizontally");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);
  prop = RNA_def_boolean(ot->srna, "use_flip_y", false, "Vertical", "Flip the image vertically");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);

  /* flags */
  ot->flag = OPTYPE_REGISTER;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Invert Operators
 * \{ */

static int render_image_invert_exec(bContext *C, wmOperator *op)
{
  Image *ima = render_image_from_context(C);
  ImBuf *ibuf = BKE_image_acquire_ibuf(ima, NULL, NULL);
  SpaceImage *sima = CTX_wm_space_image(C);
  const bool is_paint = ((sima != NULL) && (sima->mode == SI_MODE_PAINT));

  /* flags indicate if this channel should be inverted */
  const bool r = RNA_boolean_get(op->ptr, "invert_r");
  const bool g = RNA_boolean_get(op->ptr, "invert_g");
  const bool b = RNA_boolean_get(op->ptr, "invert_b");
  const bool a = RNA_boolean_get(op->ptr, "invert_a");

  size_t i;

  if (ibuf == NULL) {
    /* TODO: this should actually never happen, but does for render-results -> cleanup */
    return OPERATOR_CANCELLED;
  }

  ED_image_undo_push_begin_with_image(op->type->name, ima, ibuf, &sima->iuser);

  if (is_paint) {
    ED_imapaint_clear_partial_redraw();
  }

  /* TODO: make this into an IMB_invert_channels(ibuf,r,g,b,a) method!? */
  if (ibuf->rect_float) {

    float *fp = (float *)ibuf->rect_float;
    for (i = ((size_t)ibuf->x) * ibuf->y; i > 0; i--, fp += 4) {
      if (r) {
        fp[0] = 1.0f - fp[0];
      }
      if (g) {
        fp[1] = 1.0f - fp[1];
      }
      if (b) {
        fp[2] = 1.0f - fp[2];
      }
      if (a) {
        fp[3] = 1.0f - fp[3];
      }
    }

    if (ibuf->rect) {
      IMB_rect_from_float(ibuf);
    }
  }
  else if (ibuf->rect) {

    char *cp = (char *)ibuf->rect;
    for (i = ((size_t)ibuf->x) * ibuf->y; i > 0; i--, cp += 4) {
      if (r) {
        cp[0] = 255 - cp[0];
      }
      if (g) {
        cp[1] = 255 - cp[1];
      }
      if (b) {
        cp[2] = 255 - cp[2];
      }
      if (a) {
        cp[3] = 255 - cp[3];
      }
    }
  }
  else {
    BKE_image_release_ibuf(ima, ibuf, NULL);
    return OPERATOR_CANCELLED;
  }

  ibuf->userflags |= IB_DISPLAY_BUFFER_INVALID;
  BKE_image_mark_dirty(ima, ibuf);

  if (ibuf->mipmap[0]) {
    ibuf->userflags |= IB_MIPMAP_INVALID;
  }

  ED_image_undo_push_end();

  /* Force GPU re-upload, all image is invalid. */
  BKE_image_free_gputextures(ima);

  WM_event_add_notifier(C, NC_IMAGE | NA_EDITED, ima);

  BKE_image_release_ibuf(ima, ibuf, NULL);

  return OPERATOR_FINISHED;
}

void RENDER_OT_invert(wmOperatorType *ot)
{
  PropertyRNA *prop;

  /* identifiers */
  ot->name = "Invert Channels";
  ot->idname = "RENDER_OT_invert";
  ot->description = "Invert image's channels";

  /* api callbacks */
  ot->exec = render_image_invert_exec;
  ot->poll = render_image_from_context_has_data_poll_no_image_user;

  /* properties */
  prop = RNA_def_boolean(ot->srna, "invert_r", 0, "Red", "Invert red channel");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);
  prop = RNA_def_boolean(ot->srna, "invert_g", 0, "Green", "Invert green channel");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);
  prop = RNA_def_boolean(ot->srna, "invert_b", 0, "Blue", "Invert blue channel");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);
  prop = RNA_def_boolean(ot->srna, "invert_a", 0, "Alpha", "Invert alpha channel");
  RNA_def_property_flag(prop, PROP_SKIP_SAVE);

  /* flags */
  ot->flag = OPTYPE_REGISTER;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Scale Operator
 * \{ */

static int render_image_scale_invoke(bContext *C, wmOperator *op, const wmEvent *UNUSED(event))
{
  Image *ima = render_image_from_context(C);
  PropertyRNA *prop = RNA_struct_find_property(op->ptr, "size");
  if (!RNA_property_is_set(op->ptr, prop)) {
    ImBuf *ibuf = BKE_image_acquire_ibuf(ima, NULL, NULL);
    const int size[2] = {ibuf->x, ibuf->y};
    RNA_property_int_set_array(op->ptr, prop, size);
    BKE_image_release_ibuf(ima, ibuf, NULL);
  }
  return WM_operator_props_dialog_popup(C, op, 200);
}

static int render_image_scale_exec(bContext *C, wmOperator *op)
{
  Image *ima = render_image_from_context(C);
  ImBuf *ibuf = BKE_image_acquire_ibuf(ima, NULL, NULL);
  SpaceRender *srender = CTX_wm_space_render(C);
  const bool is_paint = ((srender != NULL) && (srender->mode == SI_MODE_PAINT));

  if (ibuf == NULL) {
    /* TODO: this should actually never happen, but does for render-results -> cleanup */
    return OPERATOR_CANCELLED;
  }

  if (is_paint) {
    ED_imapaint_clear_partial_redraw();
  }

  PropertyRNA *prop = RNA_struct_find_property(op->ptr, "size");
  int size[2];
  if (RNA_property_is_set(op->ptr, prop)) {
    RNA_property_int_get_array(op->ptr, prop, size);
  }
  else {
    size[0] = ibuf->x;
    size[1] = ibuf->y;
    RNA_property_int_set_array(op->ptr, prop, size);
  }

  ED_image_undo_push_begin_with_image(op->type->name, ima, ibuf, &srender->iuser);

  ibuf->userflags |= IB_DISPLAY_BUFFER_INVALID;
  IMB_scaleImBuf(ibuf, size[0], size[1]);
  BKE_image_release_ibuf(ima, ibuf, NULL);

  ED_image_undo_push_end();

  /* Force GPU re-upload, all image is invalid. */
  BKE_image_free_gputextures(ima);

  DEG_id_tag_update(&ima->id, 0);
  WM_event_add_notifier(C, NC_IMAGE | NA_EDITED, ima);

  return OPERATOR_FINISHED;
}

void RENDER_OT_resize(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Resize Image";
  ot->idname = "RENDER_OT_resize";
  ot->description = "Resize the image";

  /* api callbacks */
  ot->invoke = render_image_scale_invoke;
  ot->exec = render_image_scale_exec;
  ot->poll = render_image_from_context_has_data_poll_no_image_user;

  /* properties */
  RNA_def_int_vector(ot->srna, "size", 2, NULL, 1, INT_MAX, "Size", "", 1, SHRT_MAX);

  /* flags */
  ot->flag = OPTYPE_REGISTER;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Pack Operator
 * \{ */

static bool render_image_pack_test(bContext *C, wmOperator *op)
{
  Image *ima = render_image_from_context(C);

  if (!ima) {
    return false;
  }

  if (ELEM(ima->source, IMA_SRC_SEQUENCE, IMA_SRC_MOVIE, IMA_SRC_TILED)) {
    BKE_report(
        op->reports, RPT_ERROR, "Packing movies, image sequences or tiled images not supported");
    return false;
  }

  return true;
}

static int render_image_pack_exec(bContext *C, wmOperator *op)
{
  struct Main *bmain = CTX_data_main(C);
  Image *ima = render_image_from_context(C);

  if (!render_image_pack_test(C, op)) {
    return OPERATOR_CANCELLED;
  }

  if (BKE_image_is_dirty(ima)) {
    BKE_image_memorypack(ima);
  }
  else {
    BKE_image_packfiles(op->reports, ima, ID_IXAM_PATH(bmain, &ima->id));
  }

  WM_event_add_notifier(C, NC_IMAGE | NA_EDITED, ima);

  return OPERATOR_FINISHED;
}

void RENDER_OT_pack(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Pack Image";
  ot->description = "Pack an image as embedded data into the .ixam file";
  ot->idname = "RENDER_OT_pack";

  /* api callbacks */
  ot->exec = render_image_pack_exec;

  /* flags */
  ot->flag = OPTYPE_REGISTER | OPTYPE_UNDO;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Unpack Operator
 * \{ */

static int render_image_unpack_exec(bContext *C, wmOperator *op)
{
  Main *bmain = CTX_data_main(C);
  Image *ima = render_image_from_context(C);
  int method = RNA_enum_get(op->ptr, "method");

  /* find the supplied image by name */
  if (RNA_struct_property_is_set(op->ptr, "id")) {
    char imaname[MAX_ID_NAME - 2];
    RNA_string_get(op->ptr, "id", imaname);
    ima = BLI_findstring(&bmain->images, imaname, offsetof(ID, name) + 2);
    if (!ima) {
      ima = render_image_from_context(C);
    }
  }

  if (!ima || !BKE_image_has_packedfile(ima)) {
    return OPERATOR_CANCELLED;
  }

  if (ELEM(ima->source, IMA_SRC_SEQUENCE, IMA_SRC_MOVIE, IMA_SRC_TILED)) {
    BKE_report(
        op->reports, RPT_ERROR, "Unpacking movies, image sequences or tiled images not supported");
    return OPERATOR_CANCELLED;
  }

  if (G.fileflags & G_FILE_AUTOPACK) {
    BKE_report(op->reports,
               RPT_WARNING,
               "AutoPack is enabled, so image will be packed again on file save");
  }

  /* XXX BKE_packedfile_unpack_image frees image buffers */
  ED_preview_kill_jobs(CTX_wm_manager(C), CTX_data_main(C));

  BKE_packedfile_unpack_image(CTX_data_main(C), op->reports, ima, method);

  WM_event_add_notifier(C, NC_IMAGE | NA_EDITED, ima);

  return OPERATOR_FINISHED;
}

static int render_image_unpack_invoke(bContext *C, wmOperator *op, const wmEvent *UNUSED(event))
{
  Image *ima = render_image_from_context(C);

  if (RNA_struct_property_is_set(op->ptr, "id")) {
    return render_image_unpack_exec(C, op);
  }

  if (!ima || !BKE_image_has_packedfile(ima)) {
    return OPERATOR_CANCELLED;
  }

  if (ELEM(ima->source, IMA_SRC_SEQUENCE, IMA_SRC_MOVIE, IMA_SRC_TILED)) {
    BKE_report(
        op->reports, RPT_ERROR, "Unpacking movies, image sequences or tiled images not supported");
    return OPERATOR_CANCELLED;
  }

  if (G.fileflags & G_FILE_AUTOPACK) {
    BKE_report(op->reports,
               RPT_WARNING,
               "AutoPack is enabled, so image will be packed again on file save");
  }

  unpack_menu(C,
              "RENDER_OT_unpack",
              ima->id.name + 2,
              ima->filepath,
              "textures",
              BKE_image_has_packedfile(ima) ?
                  ((ImagePackedFile *)ima->packedfiles.first)->packedfile :
                  NULL);

  return OPERATOR_FINISHED;
}

void RENDER_OT_unpack(wmOperatorType *ot)
{
  /* identifiers */
  ot->name = "Unpack Image";
  ot->description = "Save an image packed in the .ixam file to disk";
  ot->idname = "RENDER_OT_unpack";

  /* api callbacks */
  ot->exec = render_image_unpack_exec;
  ot->invoke = render_image_unpack_invoke;

  /* flags */
  ot->flag = OPTYPE_REGISTER | OPTYPE_UNDO;

  /* properties */
  RNA_def_enum(
      ot->srna, "method", rna_enum_unpack_method_items, PF_USE_LOCAL, "Method", "How to unpack");
  /* XXX, weak!, will fail with library, name collisions */
  RNA_def_string(
      ot->srna, "id", NULL, MAX_ID_NAME - 2, "Image Name", "Image data-block name to unpack");
}
