// Copyright 2021 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// Author: Sergey Sharybin


#include "internal/evaluator/eval_output.h"

namespace ixam {
namespace opensubdiv {

bool is_adaptive(CpuPatchTable *patch_table)
{
  return patch_table->GetPatchArrayBuffer()[0].GetDescriptor().IsAdaptive();
}

bool is_adaptive(GLPatchTable *patch_table)
{
  return patch_table->GetPatchArrays()[0].GetDescriptor().IsAdaptive();
}

}  // namespace opensubdiv
}  // namespace ixam
