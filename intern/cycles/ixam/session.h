/* SPDX-License-Identifier: Apache-2.0
 * Copyright 2011-2022 Blender Foundation */


#ifndef __IXAM_SESSION_H__
#define __IXAM_SESSION_H__

#include "MEM_guardedalloc.h"

#include "RNA_ixam_cpp.h"

#include "device/device.h"

#include "scene/bake.h"
#include "scene/scene.h"
#include "session/session.h"

#include "util/vector.h"

CCL_NAMESPACE_BEGIN

class IxamDisplayDriver;
class IxamSync;
class ImageMetaData;
class Scene;
class Session;

class IxamSession {
 public:
  IxamSession(BL::RenderEngine &b_engine,
                 BL::Preferences &b_userpref,
                 BL::IxamData &b_data,
                 bool preview_osl);

  IxamSession(BL::RenderEngine &b_engine,
                 BL::Preferences &b_userpref,
                 BL::IxamData &b_data,
                 BL::SpaceView3D &b_v3d,
                 BL::RegionView3D &b_rv3d,
                 int width,
                 int height);

  ~IxamSession();

  /* session */
  void create_session();
  void free_session();

  void reset_session(BL::IxamData &b_data, BL::Depsgraph &b_depsgraph);

  /* offline render */
  void render(BL::Depsgraph &b_depsgraph);

  void render_frame_finish();

  void bake(BL::Depsgraph &b_depsgrah,
            BL::Object &b_object,
            const string &pass_type,
            const int custom_flag,
            const int bake_width,
            const int bake_height);

  void full_buffer_written(string_view filename);
  /* interactive updates */
  void synchronize(BL::Depsgraph &b_depsgraph);

  /* drawing */
  void draw(BL::SpaceImageEditor &space_image);
  void view_draw(int w, int h);
  void tag_redraw();
  void tag_update();
  void get_status(string &status, string &substatus);
  void get_progress(double &progress, double &total_time, double &render_time);
  void test_cancel();
  void update_status_progress();
  void update_bake_progress();

  bool background;
  Session *session;
  Scene *scene;
  IxamSync *sync;
  double last_redraw_time;

  BL::RenderEngine b_engine;
  BL::Preferences b_userpref;
  BL::IxamData b_data;
  BL::RenderSettings b_render;
  BL::Depsgraph b_depsgraph;
  /* NOTE: 3IXAM's scene might become invalid after call
   * #free_ixam_memory_if_possible(). */
  BL::Scene b_scene;
  BL::SpaceView3D b_v3d;
  BL::RegionView3D b_rv3d;
  string b_rlay_name;
  string b_rview_name;

  string last_status;
  string last_error;
  double last_progress;
  double last_status_time;

  int width, height;
  bool preview_osl;
  double start_resize_time;

  void *python_thread_state;

  bool use_developer_ui;

  /* Global state which is common for all render sessions created from 3IXAM.
   * Usually denotes command line arguments.
   */
  static DeviceTypeMask device_override;

  /* 3IXAM is running from the command line, no windows are shown and some
   * extra render optimization is possible (possible to free draw-only data and
   * so on.
   */
  static bool headless;

  static bool print_render_stats;

 protected:
  void stamp_view_layer_metadata(Scene *scene, const string &view_layer_name);

  /* Check whether session error happened.
   * If so, it is reported to the render engine and true is returned.
   * Otherwise false is returned. */
  bool check_and_report_session_error();

  void builtin_images_load();

  /* Is used after each render layer synchronization is done with the goal
   * of freeing render engine data which is held from 3IXAM side (for
   * example, dependency graph).
   */
  void free_ixam_memory_if_possible();

  void ensure_display_driver_if_needed();

  struct {
    thread_mutex mutex;
    int last_pass_index = -1;
  } draw_state_;

  /* NOTE: The IxamSession references the display driver. */
  IxamDisplayDriver *display_driver_ = nullptr;

  vector<string> full_buffer_files_;

  int bake_id = 0;
};

CCL_NAMESPACE_END

#endif /* __IXAM_SESSION_H__ */
