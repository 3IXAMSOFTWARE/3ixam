
#pragma once

#include "usd.h"
#include "usd_reader_geom.h"

#include "pxr/usd/usdGeom/nurbsCurves.h"

struct Curve;

namespace ixam::io::usd {

class USDNurbsReader : public USDGeomReader {
 protected:
  pxr::UsdGeomNurbsCurves curve_prim_;
  Curve *curve_;

 public:
  USDNurbsReader(const pxr::UsdPrim &prim,
                 const USDImportParams &import_params,
                 const ImportSettings &settings)
      : USDGeomReader(prim, import_params, settings), curve_prim_(prim), curve_(nullptr)
  {
  }

  bool valid() const override
  {
    return bool(curve_prim_);
  }

  void create_object(Main *bmain, double motionSampleTime) override;
  void read_object_data(Main *bmain, double motionSampleTime) override;

  void read_curve_sample(Curve *cu, double motionSampleTime);

  Mesh *read_mesh(struct Mesh *existing_mesh,
                  double motionSampleTime,
                  int read_flag,
                  const char **err_str) override;
};

}  // namespace ixam::io::usd
