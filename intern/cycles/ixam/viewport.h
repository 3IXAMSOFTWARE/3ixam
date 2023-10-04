

#ifndef __IXAM_VIEWPORT_H__
#define __IXAM_VIEWPORT_H__

#include "MEM_guardedalloc.h"

#include "RNA_access.h"
#include "RNA_ixam_cpp.h"
#include "RNA_types.h"

#include "scene/film.h"

CCL_NAMESPACE_BEGIN

class IxamViewportParameters {
 public:
  /* Shader. */
  bool use_scene_world;
  bool use_scene_lights;
  float studiolight_rotate_z;
  float studiolight_intensity;
  float studiolight_background_alpha;
  ustring studiolight_path;

  /* Film. */
  PassType display_pass;
  bool show_active_pixels;

  IxamViewportParameters();
  IxamViewportParameters(BL::SpaceView3D &b_v3d, bool use_developer_ui);

  /* Check whether any of shading related settings are different from the given parameters. */
  bool shader_modified(const IxamViewportParameters &other) const;

  /* Check whether any of film related settings are different from the given parameters. */
  bool film_modified(const IxamViewportParameters &other) const;

  /* Check whether any of settings are different from the given parameters. */
  bool modified(const IxamViewportParameters &other) const;

  /* Returns truth when a custom shader defined by the viewport is to be used instead of the
   * regular background shader or scene light. */
  bool use_custom_shader() const;
};

CCL_NAMESPACE_END

#endif