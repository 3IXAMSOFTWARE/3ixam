#pragma IXAM_REQUIRE(gpu_shader_colorspace_lib.glsl)

void main()
{
  fragColor = ixam_srgb_to_framebuffer_space(color);
}
