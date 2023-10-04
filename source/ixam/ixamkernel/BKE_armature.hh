#pragma once

/** \file
 * \ingroup bke
 */
#ifndef __cplusplus
#  error This is a C++ only header.
#endif

#include "BKE_armature.h"

#include "BLI_function_ref.hh"
#include "BLI_set.hh"

namespace ixam::bke {

struct SelectedBonesResult {
  bool all_bones_selected = true;
  bool no_bones_selected = true;
};

using SelectedBoneCallback = ixam::FunctionRef<void(Bone *bone)>;
SelectedBonesResult BKE_armature_find_selected_bones(const bArmature *armature,
                                                     SelectedBoneCallback callback);

using BoneNameSet = ixam::Set<std::string>;
/**
 * Return a set of names of the selected bones. An empty set means "ignore bone
 * selection", which either means all bones are selected, or none are.
 */
BoneNameSet BKE_armature_find_selected_bone_names(const bArmature *armature);

};  // namespace ixam::bke
