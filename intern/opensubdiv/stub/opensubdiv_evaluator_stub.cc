// Copyright 2018 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// Author: Sergey Sharybin


#include "opensubdiv_evaluator_capi.h"

#include <cstddef>

OpenSubdiv_Evaluator *openSubdiv_createEvaluatorFromTopologyRefiner(
    struct OpenSubdiv_TopologyRefiner * /*topology_refiner*/,
    eOpenSubdivEvaluator /*evaluator_type*/,
    OpenSubdiv_EvaluatorCache * /*evaluator_cache*/)
{
  return NULL;
}

void openSubdiv_deleteEvaluator(OpenSubdiv_Evaluator * /*evaluator*/)
{
}

OpenSubdiv_EvaluatorCache *openSubdiv_createEvaluatorCache(eOpenSubdivEvaluator /*evaluator_type*/)
{
  return NULL;
}

void openSubdiv_deleteEvaluatorCache(OpenSubdiv_EvaluatorCache * /*evaluator_cache*/)
{
}

const char *openSubdiv_getGLSLPatchBasisSource()
{
  return NULL;
}
