

#include "util/transform.h"

CCL_NAMESPACE_BEGIN

void transform_inverse_cpu_avx2(const Transform &tfm, Transform &itfm)
{
  itfm = transform_inverse_impl(tfm);
}

CCL_NAMESPACE_END
