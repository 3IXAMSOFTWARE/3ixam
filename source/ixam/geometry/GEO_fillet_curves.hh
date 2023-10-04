

#pragma once

#include "BLI_function_ref.hh"
#include "BLI_index_mask.hh"

#include "BKE_curves.hh"

namespace ixam::geometry {

bke::CurvesGeometry fillet_curves_poly(const bke::CurvesGeometry &src_curves,
                                       IndexMask curve_selection,
                                       const VArray<float> &radius,
                                       const VArray<int> &counts,
                                       bool limit_radius);

bke::CurvesGeometry fillet_curves_bezier(const bke::CurvesGeometry &src_curves,
                                         IndexMask curve_selection,
                                         const VArray<float> &radius,
                                         bool limit_radius);

}  // namespace ixam::geometry
