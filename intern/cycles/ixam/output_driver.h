

#pragma once

#include "MEM_guardedalloc.h"

#include "RNA_ixam_cpp.h"

#include "session/output_driver.h"

CCL_NAMESPACE_BEGIN

class IxamOutputDriver : public OutputDriver {
 public:
  explicit IxamOutputDriver(BL::RenderEngine &b_engine);
  ~IxamOutputDriver();

  virtual void write_render_tile(const Tile &tile) override;
  virtual bool update_render_tile(const Tile &tile) override;
  virtual bool read_render_tile(const Tile &tile) override;

 protected:
  BL::RenderEngine b_engine_;
};

CCL_NAMESPACE_END
