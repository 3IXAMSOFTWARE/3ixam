

/** \file
 * \ingroup gpu
 */

#include "vk_query.hh"

namespace ixam::gpu {

void VKQueryPool::init(GPUQueryType /*type*/)
{
}

void VKQueryPool::begin_query()
{
}

void VKQueryPool::end_query()
{
}

void VKQueryPool::get_occlusion_result(MutableSpan<uint32_t> /*r_values*/)
{
}

}  // namespace ixam::gpu