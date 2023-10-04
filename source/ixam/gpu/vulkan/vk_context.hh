

/** \file
 * \ingroup gpu
 */

#pragma once

#include "gpu_context_private.hh"

namespace ixam::gpu {

class VKContext : public Context {
 public:
  VKContext()
  {
  }

  void activate() override;
  void deactivate() override;
  void begin_frame() override;
  void end_frame() override;

  void flush() override;
  void finish() override;

  void memory_statistics_get(int *total_mem, int *free_mem) override;

  void debug_group_begin(const char *, int) override;
  void debug_group_end() override;
};

}  // namespace ixam::gpu