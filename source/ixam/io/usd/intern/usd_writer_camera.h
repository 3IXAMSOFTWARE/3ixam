
#pragma once

#include "usd_writer_abstract.h"

namespace ixam::io::usd {

/* Writer for writing camera data to UsdGeomCamera. */
class USDCameraWriter : public USDAbstractWriter {
 public:
  USDCameraWriter(const USDExporterContext &ctx);

 protected:
  virtual bool is_supported(const HierarchyContext *context) const override;
  virtual void do_write(HierarchyContext &context) override;
};

}  // namespace ixam::io::usd
