
#pragma IXAM_REQUIRE(common_view_clipping_lib.glsl)
#pragma IXAM_REQUIRE(common_view_lib.glsl)

void main()
{
  vec3 world_pos = point_object_to_world(pos);
  gl_Position = point_world_to_ndc(world_pos);
  view_clipping_distances(world_pos);
}
