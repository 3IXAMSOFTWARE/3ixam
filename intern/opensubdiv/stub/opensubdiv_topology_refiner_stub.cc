

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