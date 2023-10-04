

#pragma once

#include "COM_MultiThreadedOperation.h"

namespace ixam::compositor {

/**
 * This operation will apply a mask to its input image.
 *
 * `output color.rgba = input color.rgba * input alpha`
 */
class SetAlphaMultiplyOperation : public MultiThreadedOperation {
 private:
  SocketReader *input_color_;
  SocketReader *input_alpha_;

 public:
  SetAlphaMultiplyOperation();

  void execute_pixel_sampled(float output[4], float x, float y, PixelSampler sampler) override;

  void init_execution() override;
  void deinit_execution() override;

  void update_memory_buffer_partial(MemoryBuffer *output,
                                    const rcti &area,
                                    Span<MemoryBuffer *> inputs) override;
};

}  // namespace ixam::compositor
