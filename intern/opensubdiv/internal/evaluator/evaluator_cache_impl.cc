// Copyright 2021 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License


#include "internal/evaluator/evaluator_cache_impl.h"

#include "internal/evaluator/eval_output_gpu.h"

OpenSubdiv_EvaluatorCacheImpl::OpenSubdiv_EvaluatorCacheImpl()
{
}

OpenSubdiv_EvaluatorCacheImpl::~OpenSubdiv_EvaluatorCacheImpl()
{
  delete static_cast<ixam::opensubdiv::GpuEvalOutput::EvaluatorCache *>(eval_cache);
}

OpenSubdiv_EvaluatorCacheImpl *openSubdiv_createEvaluatorCacheInternal(
    eOpenSubdivEvaluator evaluator_type)
{
  if (evaluator_type != eOpenSubdivEvaluator::OPENSUBDIV_EVALUATOR_GPU) {
    return nullptr;
  }
  OpenSubdiv_EvaluatorCacheImpl *evaluator_cache;
  evaluator_cache = new OpenSubdiv_EvaluatorCacheImpl;
  ixam::opensubdiv::GpuEvalOutput::EvaluatorCache *eval_cache;
  eval_cache = new ixam::opensubdiv::GpuEvalOutput::EvaluatorCache();
  evaluator_cache->eval_cache = eval_cache;
  return evaluator_cache;
}

void openSubdiv_deleteEvaluatorCacheInternal(OpenSubdiv_EvaluatorCacheImpl *evaluator_cache)
{
  delete evaluator_cache;
}
