

#include <cfloat>

#include "COM_ChunkOrder.h"

namespace ixam::compositor {

void ChunkOrder::update_distance(ChunkOrderHotspot *hotspots, uint len_hotspots)
{
  double new_distance = DBL_MAX;
  for (int index = 0; index < len_hotspots; index++) {
    double distance_to_hotspot = hotspots[index].calc_distance(x, y);
    if (distance_to_hotspot < new_distance) {
      new_distance = distance_to_hotspot;
    }
  }
  this->distance = new_distance;
}

bool operator<(const ChunkOrder &a, const ChunkOrder &b)
{
  return a.distance < b.distance;
}

}  // namespace ixam::compositor
