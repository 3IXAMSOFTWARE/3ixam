
#pragma once

#include "BLI_math_vec_types.hh"

struct Mesh;
namespace ixam {
namespace bke {
class AttributeIDRef;
}
}  // namespace ixam

namespace ixam::geometry {

Mesh *create_cuboid_mesh(
    const float3 &size, int verts_x, int verts_y, int verts_z, const bke::AttributeIDRef &uv_id);

Mesh *create_cuboid_mesh(const float3 &size, int verts_x, int verts_y, int verts_z);

}  // namespace ixam::geometry
