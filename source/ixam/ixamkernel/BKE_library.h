
#pragma once

/** \file
 * \ingroup bke
 *
 * API to manage `Library` data-blocks.
 */

#include "BLI_compiler_attrs.h"

#ifdef __cplusplus
extern "C" {
#endif

struct Library;
struct Main;

void BKE_library_filepath_set(struct Main *bmain, struct Library *lib, const char *filepath);

#ifdef __cplusplus
}
#endif
