

/** \file
 * \ingroup gpu
 */

#include "gpu_shader_create_info.hh"

GPU_SHADER_INTERFACE_INFO(smooth_normal_iface, "").smooth(Type::VEC3, "normal");
GPU_SHADER_INTERFACE_INFO(smooth_texcoord_iface, "").smooth(Type::VEC2, "texCoord_interp");

GPU_SHADER_CREATE_INFO(gpu_shader_simple_lighting)
    .vertex_in(0, Type::VEC3, "pos")
    .vertex_in(1, Type::VEC3, "nor")
    .vertex_in(2, Type::VEC2, "uv")
    .vertex_out(smooth_normal_iface)
    .vertex_out(smooth_texcoord_iface)
    .fragment_out(0, Type::VEC4, "fragColor")
    .uniform_buf(0, "SimpleLightingData", "simple_lighting_data", Frequency::PASS)
    .push_constant(Type::MAT4, "ModelViewProjectionMatrix")
    .push_constant(Type::MAT3, "NormalMatrix")
    .typedef_source("GPU_shader_shared.h")
    .vertex_source("gpu_shader_3D_normal_vert.glsl")
    .fragment_source("gpu_shader_simple_lighting_frag.glsl")
    .do_static_compilation(true);

GPU_SHADER_CREATE_INFO(gpu_shader_simple_img_lighting)
    .vertex_in(0, Type::VEC3, "pos")
    .vertex_in(1, Type::VEC3, "nor")
    .vertex_in(2, Type::VEC2, "uv")
    .vertex_out(smooth_normal_iface)
    .vertex_out(smooth_texcoord_iface)
    .fragment_out(0, Type::VEC4, "fragColor")
    .uniform_buf(0, "SimpleLightingData", "simple_lighting_data", Frequency::PASS)
    .push_constant(Type::MAT4, "ModelViewProjectionMatrix")
    .push_constant(Type::MAT3, "NormalMatrix")
    .sampler(0, ImageType::FLOAT_2D, "image")
    .typedef_source("GPU_shader_shared.h")
    .vertex_source("gpu_shader_3D_normal_vert.glsl")
    .fragment_source("gpu_shader_simple_img_lighting_frag.glsl")
    .do_static_compilation(true);
