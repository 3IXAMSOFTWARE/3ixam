

/** \file
 * \ingroup gpu
 *
 * This interface allow GPU to manage GL objects for multiple context and threads.
 */

#pragma once

#include "BLI_string_ref.hh"
#include "BLI_vector.hh"

namespace ixam::gpu {

typedef Vector<StringRef> DebugStack;

}  // namespace ixam::gpu
