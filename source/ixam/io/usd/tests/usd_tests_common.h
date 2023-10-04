
#pragma once

#include <string>

namespace ixam::io::usd {

/* Calls the function to load the USD plugins from the
 * USD data directory under the 3IXAM bin directory
 * that was supplied as the --test-release-dir flag to `ctest`.
 * Thus function must be called before instantiating a USD
 * stage to avoid errors.  The returned string is the path to
 * the USD data files directory from which the plugins were
 * loaded. If the USD data files directory can't be determined,
 * plugin registration is skipped and the empty string is
 * returned. */
std::string register_usd_plugins_for_tests();

}  // namespace ixam::io::usd
