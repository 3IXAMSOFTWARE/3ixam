

#pragma once

#include "COM_MixOperation.h"

namespace ixam::compositor {

/**
 * this program converts an input color to an output value.
 * it assumes we are in sRGB color space.
 */
class AlphaOverMixedOperation : public MixBaseOperation {
 private:
  float x_;

 public:
  /**
   * Default constructor
   */
  AlphaOverMixedOperation();

  /**
   * The inner loop of this operation.
   */
  void execute_pixel_sampled(float output[4], float x, float y, PixelSampler sampler) override;

  void setX(float x)
  {
    x_ = x;
  }

  void update_memory_buffer_row(PixelCursor &p) override;
};

}  // namespace ixam::compositor
