

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
