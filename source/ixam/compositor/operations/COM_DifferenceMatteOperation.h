

#pragma once

#include "COM_MultiThreadedOperation.h"

namespace ixam::compositor {

/**
 * this program converts an input color to an output value.
 * it assumes we are in sRGB color space.
 */
class DifferenceMatteOperation : public MultiThreadedOperation {
 private:
  NodeChroma *settings_;
  SocketReader *input_image1_program_;
  SocketReader *input_image2_program_;

 public:
  /**
   * Default constructor
   */
  DifferenceMatteOperation();

  /**
   * The inner loop of this operation.
   */
  void execute_pixel_sampled(float output[4], float x, float y, PixelSampler sampler) override;

  void init_execution() override;
  void deinit_execution() override;

  void set_settings(NodeChroma *node_chroma)
  {
    settings_ = node_chroma;
  }

  void update_memory_buffer_partial(MemoryBuffer *output,
                                    const rcti &area,
                                    Span<MemoryBuffer *> inputs) override;
};

}  // namespace ixam::compositor
