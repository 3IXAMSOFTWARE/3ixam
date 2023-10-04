

#ifdef WITH_METAL

#  include "device/metal/bvh.h"

CCL_NAMESPACE_BEGIN

BVH *bvh_metal_create(const BVHParams &params,
                      const vector<Geometry *> &geometry,
                      const vector<Object *> &objects,
                      Device *device)
{
  return new BVHMetal(params, geometry, objects, device);
}

CCL_NAMESPACE_END

#endif /* WITH_METAL */