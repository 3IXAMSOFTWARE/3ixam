

#include "internal/topology/topology_refiner_impl.h"

namespace ixam {
namespace opensubdiv {

TopologyRefinerImpl::TopologyRefinerImpl() : topology_refiner(nullptr)
{
}

TopologyRefinerImpl::~TopologyRefinerImpl()
{
  delete topology_refiner;
}

}  // namespace opensubdiv
}  // namespace ixam
