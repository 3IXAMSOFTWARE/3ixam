

/** \file
 * \ingroup gpu
 */

#pragma once

#include "gpu_index_buffer_private.hh"

namespace ixam::gpu {

class VKIndexBuffer : public IndexBuf {
 public:
  void upload_data() override;

  void bind_as_ssbo(uint binding) override;

  const uint32_t *read() const override;

  void update_sub(uint start, uint len, const void *data) override;

 private:
  void strip_restart_indices() override;
};

}  // namespace ixam::gpu