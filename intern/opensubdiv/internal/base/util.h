// Copyright 2013 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License


#ifndef OPENSUBDIV_BASE_UTIL_H_
#define OPENSUBDIV_BASE_UTIL_H_

#include "internal/base/type.h"

namespace ixam {
namespace opensubdiv {

void stringSplit(vector<string> *tokens,
                 const string &str,
                 const string &separators,
                 bool skip_empty);

}  // namespace opensubdiv
}  // namespace ixam

#endif  // OPENSUBDIV_BASE_UTIL_H_
