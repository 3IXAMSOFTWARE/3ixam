
#pragma once

#include "usd.h"

#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/common.h>

struct Depsgraph;
struct Main;

namespace ixam::io::usd {

class USDHierarchyIterator;

struct USDExporterContext {
  Main *bmain;
  Depsgraph *depsgraph;
  const pxr::UsdStageRefPtr stage;
  const pxr::SdfPath usd_path;
  const USDHierarchyIterator *hierarchy_iterator;
  const USDExportParams &export_params;
};

}  // namespace ixam::io::usd
