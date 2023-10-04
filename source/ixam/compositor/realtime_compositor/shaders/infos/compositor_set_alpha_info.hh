
#include "gpu_shader_create_info.hh"

GPU_SHADER_CREATE_INFO(compositor_set_alpha)
    .local_group_size(16, 16)
    .sampler(0, ImageType::FLOAT_2D, "image_tx")
    .sampler(1, ImageType::FLOAT_2D, "alpha_tx")
    .image(0, GPU_RGBA16F, Qualifier::WRITE, ImageType::FLOAT_2D, "output_img")
    .compute_source("compositor_set_alpha.glsl")
    .do_static_compilation(true);
