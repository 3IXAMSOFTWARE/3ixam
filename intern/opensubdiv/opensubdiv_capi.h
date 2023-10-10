// Copyright 2013 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// Author: Sergey Sharybin


#ifndef OPENSUBDIV_CAPI_H_
#define OPENSUBDIV_CAPI_H_

#include "opensubdiv_capi_type.h"

#ifdef __cplusplus
extern "C" {
#endif

// Global initialization/deinitialization.
//
// Supposed to be called from main thread.
void openSubdiv_init(void);
void openSubdiv_cleanup(void);

int openSubdiv_getVersionHex(void);

#ifdef __cplusplus
}
#endif

#endif  // OPENSUBDIV_CAPI_H_
