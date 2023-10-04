

#pragma once

#include "COM_NodeOperation.h"

namespace ixam::compositor {

/**
 * this program converts an input color to an output Sampler.
 * it assumes we are in sRGB color space.
 */
class SetSamplerOperation : public NodeOperation {
 private:
  PixelSampler sampler_;
  SocketReader *reader_;

 public:
  /**
   * Default constructor
   */
  SetSamplerOperation();

  void set_sampler(PixelSampler sampler)
  {
    sampler_ = sampler;
  }

  /**
   * The inner loop of this operation.
   */
  void execute_pixel_sampled(float output[4], float x, float y, PixelSampler sampler) override;
  void init_execution() override;
  void deinit_execution() override;
};

}  // namespace ixam::compositor