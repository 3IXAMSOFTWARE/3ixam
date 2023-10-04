

#pragma once

#include "IO_stl.h"

namespace ixam::io::stl {

void stl_import_report_error(FILE *file);

/* Main import function used from within 3IXAM. */
void importer_main(bContext *C, const STLImportParams &import_params);

/* Used from tests, where full bContext does not exist. */
void importer_main(Main *bmain,
                   Scene *scene,
                   ViewLayer *view_layer,
                   const STLImportParams &import_params);

}  // namespace ixam::io::stl
