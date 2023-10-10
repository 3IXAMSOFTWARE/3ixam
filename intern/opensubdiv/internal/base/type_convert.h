// Copyright 2018 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// Author: Sergey Sharybin


#ifndef OPENSUBDIV_BASE_TYPE_CONVERT_H_
#define OPENSUBDIV_BASE_TYPE_CONVERT_H_

#ifdef _MSC_VER
#  include <iso646.h>
#endif

#include <opensubdiv/sdc/options.h>
#include <opensubdiv/sdc/types.h>

#include "opensubdiv_capi_type.h"

struct OpenSubdiv_Converter;

namespace ixam {
namespace opensubdiv {

// Convert scheme type from C-API enum to an OpenSubdiv native enum.
OpenSubdiv::Sdc::SchemeType getSchemeTypeFromCAPI(OpenSubdiv_SchemeType type);

// Convert face-varying interpolation type from C-API to an OpenSubdiv
// native enum.
OpenSubdiv::Sdc::Options::FVarLinearInterpolation getFVarLinearInterpolationFromCAPI(
    OpenSubdiv_FVarLinearInterpolation linear_interpolation);

// Similar to above, just other way around.
OpenSubdiv_FVarLinearInterpolation getCAPIFVarLinearInterpolationFromOSD(
    OpenSubdiv::Sdc::Options::FVarLinearInterpolation linear_interpolation);

OpenSubdiv::Sdc::Options::VtxBoundaryInterpolation getVtxBoundaryInterpolationFromCAPI(
    OpenSubdiv_VtxBoundaryInterpolation boundary_interpolation);

}  // namespace opensubdiv
}  // namespace ixam

#endif  // OPENSUBDIV_BASE_TYPE_CONVERT_H_
