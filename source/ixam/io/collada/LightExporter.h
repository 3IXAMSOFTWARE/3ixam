

#pragma once

#include "COLLADASWLibraryLights.h"
#include "COLLADASWStreamWriter.h"

#include "DNA_light_types.h"
#include "DNA_object_types.h"
#include "DNA_scene_types.h"

#include "ExportSettings.h"

class LightsExporter : COLLADASW::LibraryLights {
 public:
  LightsExporter(COLLADASW::StreamWriter *sw, BCExportSettings &export_settings);
  void exportLights(Scene *sce);
  void operator()(Object *ob);

 private:
  bool exportIxamProfile(COLLADASW::Light &cla, Light *la);
  BCExportSettings &export_settings;
};
