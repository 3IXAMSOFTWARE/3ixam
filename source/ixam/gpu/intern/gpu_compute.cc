

#include "GPU_compute.h"

#include "gpu_backend.hh"

void GPU_compute_dispatch(GPUShader *shader,
                          uint groups_x_len,
                          uint groups_y_len,
                          uint groups_z_len)
{
  ixam::gpu::GPUBackend &gpu_backend = *ixam::gpu::GPUBackend::get();
  GPU_shader_bind(shader);
  gpu_backend.compute_dispatch(groups_x_len, groups_y_len, groups_z_len);
}

void GPU_compute_dispatch_indirect(GPUShader *shader, GPUStorageBuf *indirect_buf_)
{
  ixam::gpu::GPUBackend &gpu_backend = *ixam::gpu::GPUBackend::get();
  ixam::gpu::StorageBuf *indirect_buf = reinterpret_cast<ixam::gpu::StorageBuf *>(
      indirect_buf_);

  GPU_shader_bind(shader);
  gpu_backend.compute_dispatch_indirect(indirect_buf);
}
