

#include "COM_CurveBaseOperation.h"

#include "BKE_colortools.h"

namespace ixam::compositor {

CurveBaseOperation::CurveBaseOperation()
{
  curve_mapping_ = nullptr;
  flags_.can_be_constant = true;
}

CurveBaseOperation::~CurveBaseOperation()
{
  if (curve_mapping_) {
    BKE_curvemapping_free(curve_mapping_);
    curve_mapping_ = nullptr;
  }
}

void CurveBaseOperation::init_execution()
{
  BKE_curvemapping_init(curve_mapping_);
}
void CurveBaseOperation::deinit_execution()
{
  if (curve_mapping_) {
    BKE_curvemapping_free(curve_mapping_);
    curve_mapping_ = nullptr;
  }
}

void CurveBaseOperation::set_curve_mapping(const CurveMapping *mapping)
{
  /* duplicate the curve to avoid glitches while drawing, see bug T32374. */
  if (curve_mapping_) {
    BKE_curvemapping_free(curve_mapping_);
  }
  curve_mapping_ = BKE_curvemapping_copy(mapping);
}

}  // namespace ixam::compositor