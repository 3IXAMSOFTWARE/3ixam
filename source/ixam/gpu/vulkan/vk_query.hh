

/** \file
 * \ingroup gpu
 */

#pragma once

#include "gpu_query.hh"

namespace ixam::gpu {

class VKQueryPool : public QueryPool {
 public:
  void init(GPUQueryType type) override;
  void begin_query() override;
  void end_query() override;
  void get_occlusion_result(MutableSpan<uint32_t> r_values) override;
};

}  // namespace ixam::gpu