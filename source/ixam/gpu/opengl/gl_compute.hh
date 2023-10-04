

#pragma once

namespace ixam::gpu {

class GLCompute {
 public:
  static void dispatch(int group_x_len, int group_y_len, int group_z_len);
};

}  // namespace ixam::gpu
