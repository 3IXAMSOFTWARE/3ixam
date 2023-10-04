

/** \file
 * \ingroup gpu
 */

#include "gpu_shader_create_info.hh"

GPU_SHADER_INTERFACE_INFO(gpu_shader_billboard_iface, "interp")
    .no_perspective(Type::FLOAT, "smoothline");

GPU_SHADER_CREATE_INFO(gpu_shader_billboard)
    .define("SMOOTH_WIDTH", "1.0")
    .vertex_in(0, Type::VEC4, "pos")
    .geometry_out(gpu_shader_billboard_iface)
    .fragment_out(0, Type::VEC4, "fragColor")
    .geometry_layout(PrimitiveIn::LINES, PrimitiveOut::TRIANGLE_STRIP, 4)
    .push_constant(Type::MAT4, "ModelViewMatrix")
    .push_constant(Type::VEC4, "color")
    .push_constant(Type::FLOAT, "scale")
    .push_constant(Type::VEC2, "viewportSize")
    .push_constant(Type::FLOAT, "lineWidth")
    .push_constant(Type::BOOL, "lineSmooth")
    .vertex_source("gpu_shader_billboard_vert.glsl")
    .geometry_source("gpu_shader_billboard_geom.glsl")
    .fragment_source("gpu_shader_billboard_frag.glsl")
    .additional_info("gpu_srgb_to_framebuffer_space", "draw_view")
    .do_static_compilation(true);
