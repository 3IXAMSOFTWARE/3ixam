

#pragma once

#include "COM_MultiThreadedOperation.h"

namespace ixam::compositor {

class GammaCorrectOperation : public MultiThreadedOperation {
 private:
  /**
   * Cached reference to the input_program
   */
  SocketReader *input_program_;

 public:
  GammaCorrectOperation();

  /**
   * The inner loop of this operation.
   */
  void execute_pixel_sampled(float output[4], float x, float y, PixelSampler sampler) override;

  /**
   * Initialize the execution
   */
  void init_execution() override;

  /**
   * Deinitialize the execution
   */
  void deinit_execution() override;

  void update_memory_buffer_partial(MemoryBuffer *output,
                                    const rcti &area,
                                    Span<MemoryBuffer *> inputs) override;
};

class GammaUncorrectOperation : public MultiThreadedOperation {
 private:
  /**
   * Cached reference to the input_program
   */
  SocketReader *input_program_;

 public:
  GammaUncorrectOperation();

  /**
   * The inner loop of this operation.
   */
  void execute_pixel_sampled(float output[4], float x, float y, PixelSampler sampler) override;

  /**
   * Initialize the execution
   */
  void init_execution() override;

  /**
   * Deinitialize the execution
   */
  void deinit_execution() override;

  void update_memory_buffer_partial(MemoryBuffer *output,
                                    const rcti &area,
                                    Span<MemoryBuffer *> inputs) override;
};

}  // namespace ixam::compositor
