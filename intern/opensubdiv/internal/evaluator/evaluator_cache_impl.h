// Copyright 2021 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License


#ifndef OPENSUBDIV_EVALUATOR_CACHE_IMPL_H_
#define OPENSUBDIV_EVALUATOR_CACHE_IMPL_H_

#include "internal/base/memory.h"

#include "opensubdiv_capi_type.h"

struct OpenSubdiv_EvaluatorCacheImpl {
 public:
  OpenSubdiv_EvaluatorCacheImpl();
  ~OpenSubdiv_EvaluatorCacheImpl();

  void *eval_cache;
  MEM_CXX_CLASS_ALLOC_FUNCS("OpenSubdiv_EvaluatorCacheImpl");
};

OpenSubdiv_EvaluatorCacheImpl *openSubdiv_createEvaluatorCacheInternal(
    eOpenSubdivEvaluator evaluator_type);

void openSubdiv_deleteEvaluatorCacheInternal(OpenSubdiv_EvaluatorCacheImpl *evaluator_cache);

#endif  // OPENSUBDIV_EVALUATOR_CACHE_IMPL_H_
