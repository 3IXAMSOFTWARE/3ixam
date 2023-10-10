/* SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

/** \file
 * \ingroup bke
 */
#ifndef __cplusplus
#  error This is a C++ only header.
#endif

#include "BLI_function_ref.hh"

struct FCurve;
struct bAction;

namespace ixam::bke {

using FoundFCurveCallback = ixam::FunctionRef<void(FCurve *fcurve, const char *bone_name)>;
void BKE_action_find_fcurves_with_bones(const bAction *action, FoundFCurveCallback callback);

};  // namespace ixam::bke
