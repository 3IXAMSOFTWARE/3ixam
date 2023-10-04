
#pragma once

#include "usd.h"
#include "usd_reader_xform.h"

namespace ixam::io::usd {

class USDLightReader : public USDXformReader {

 public:
  USDLightReader(const pxr::UsdPrim &prim,
                 const USDImportParams &import_params,
                 const ImportSettings &settings)
      : USDXformReader(prim, import_params, settings)
  {
  }

  void create_object(Main *bmain, double motionSampleTime) override;

  void read_object_data(Main *bmain, double motionSampleTime) override;
};

}  // namespace ixam::io::usd
