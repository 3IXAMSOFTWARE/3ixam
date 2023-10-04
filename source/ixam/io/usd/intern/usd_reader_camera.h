
#pragma once

#include "usd.h"
#include "usd_reader_xform.h"

namespace ixam::io::usd {

class USDCameraReader : public USDXformReader {

 public:
  USDCameraReader(const pxr::UsdPrim &object,
                  const USDImportParams &import_params,
                  const ImportSettings &settings)
      : USDXformReader(object, import_params, settings)
  {
  }

  void create_object(Main *bmain, double motionSampleTime) override;
  void read_object_data(Main *bmain, double motionSampleTime) override;
};

}  // namespace ixam::io::usd
