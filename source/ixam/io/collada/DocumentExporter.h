/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include "IxamContext.h"
#include "collada.h"
#include "collada_utils.h"

#include "DNA_customdata_types.h"

class DocumentExporter {
 public:
  DocumentExporter(IxamContext &ixam_context, ExportSettings *export_settings);
  int exportCurrentScene();
  void exportScenes(const char *filename);

 private:
  IxamContext &ixam_context;
  BCExportSettings export_settings;
  KeyImageMap key_image_map;
};
