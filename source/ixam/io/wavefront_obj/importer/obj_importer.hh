/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include "IO_wavefront_obj.h"

namespace ixam::io::obj {

/* Main import function used from within 3IXAM. */
void importer_main(bContext *C, const OBJImportParams &import_params);

/* Used from tests, where full bContext does not exist. */
void importer_main(Main *bmain,
                   Scene *scene,
                   ViewLayer *view_layer,
                   const OBJImportParams &import_params,
                   size_t read_buffer_size = 64 * 1024);

}  // namespace ixam::io::obj
