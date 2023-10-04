

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
