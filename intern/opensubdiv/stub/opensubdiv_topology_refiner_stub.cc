// Copyright 2018 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// Author: Sergey Sharybin


#include "opensubdiv_topology_refiner_capi.h"

#include <cstddef>

OpenSubdiv_TopologyRefiner *openSubdiv_createTopologyRefinerFromConverter(
    OpenSubdiv_Converter * /*converter*/, const OpenSubdiv_TopologyRefinerSettings * /*settings*/)
{
  return NULL;
}

void openSubdiv_deleteTopologyRefiner(OpenSubdiv_TopologyRefiner * /*topology_refiner*/)
{
}

bool openSubdiv_topologyRefinerCompareWithConverter(
    const OpenSubdiv_TopologyRefiner * /*topology_refiner*/,
    const OpenSubdiv_Converter * /*converter*/)
{
  return false;
}
