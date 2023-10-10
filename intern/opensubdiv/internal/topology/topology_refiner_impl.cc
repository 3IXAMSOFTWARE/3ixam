// Copyright 2016 Blender Foundation. All rights reserved.
// modify it under the terms of the GNU General Public License
// of the License, or (at your option) any later version.
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License
// Author: Sergey Sharybin


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
