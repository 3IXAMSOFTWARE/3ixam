

#pragma once

#include "COM_GlareBaseOperation.h"
#include "COM_NodeOperation.h"
#include "DNA_node_types.h"

namespace ixam::compositor {

class GlareStreaksOperation : public GlareBaseOperation {
 public:
  GlareStreaksOperation() : GlareBaseOperation()
  {
  }

 protected:
  void generate_glare(float *data, MemoryBuffer *input_tile, const NodeGlare *settings) override;
};

}  // namespace ixam::compositor