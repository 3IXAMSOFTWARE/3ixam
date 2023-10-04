

#pragma once

#include "COM_DistanceRGBMatteOperation.h"
#include "COM_MixOperation.h"

namespace ixam::compositor {

/**
 * this program converts an input color to an output value.
 * it assumes we are in sRGB color space.
 */
class DistanceYCCMatteOperation : public DistanceRGBMatteOperation {
 protected:
  float calculate_distance(const float key[4], const float image[4]) override;
};

}  // namespace ixam::compositor
