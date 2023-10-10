/* SPDX-License-Identifier: Apache-2.0
 * Copyright 2011-2022 Blender Foundation */


#ifndef __IXAM_OBJECT_CULL_H__
#define __IXAM_OBJECT_CULL_H__

#include "ixam/sync.h"
#include "util/types.h"

CCL_NAMESPACE_BEGIN

class Scene;

class IxamObjectCulling {
 public:
  IxamObjectCulling(Scene *scene, BL::Scene &b_scene);

  void init_object(Scene *scene, BL::Object &b_ob);
  bool test(Scene *scene, BL::Object &b_ob, Transform &tfm);

 private:
  bool test_camera(Scene *scene, float3 bb[8]);
  bool test_distance(Scene *scene, float3 bb[8]);

  bool use_scene_camera_cull_;
  bool use_camera_cull_;
  float camera_cull_margin_;
  bool use_scene_distance_cull_;
  bool use_distance_cull_;
  float distance_cull_margin_;
};

CCL_NAMESPACE_END

#endif /* __IXAM_OBJECT_CULL_H__ */
