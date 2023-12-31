/* SPDX-License-Identifier: Apache-2.0
 * Copyright 2021-2022 Blender Foundation */


#pragma once

#include <atomic>

#include "MEM_guardedalloc.h"

#include "RNA_ixam_cpp.h"

#include "session/display_driver.h"

#include "util/thread.h"
#include "util/unique_ptr.h"
#include "util/vector.h"

CCL_NAMESPACE_BEGIN

/* Base class of shader used for display driver rendering. */
class IxamDisplayShader {
 public:
  static constexpr const char *position_attribute_name = "pos";
  static constexpr const char *tex_coord_attribute_name = "texCoord";

  /* Create shader implementation suitable for the given render engine and scene configuration. */
  static unique_ptr<IxamDisplayShader> create(BL::RenderEngine &b_engine, BL::Scene &b_scene);

  IxamDisplayShader() = default;
  virtual ~IxamDisplayShader() = default;

  virtual void bind(int width, int height) = 0;
  virtual void unbind() = 0;

  /* Get attribute location for position and texture coordinate respectively.
   * NOTE: The shader needs to be bound to have access to those. */
  virtual int get_position_attrib_location();
  virtual int get_tex_coord_attrib_location();

 protected:
  /* Get program of this display shader.
   * NOTE: The shader needs to be bound to have access to this. */
  virtual uint get_shader_program() = 0;

  /* Cached values of various OpenGL resources. */
  int position_attribute_location_ = -1;
  int tex_coord_attribute_location_ = -1;
};

/* Implementation of display rendering shader used in the case when render engine does not support
 * display space shader. */
class IxamFallbackDisplayShader : public IxamDisplayShader {
 public:
  virtual void bind(int width, int height) override;
  virtual void unbind() override;

 protected:
  virtual uint get_shader_program() override;

  void create_shader_if_needed();
  void destroy_shader();

  uint shader_program_ = 0;
  int image_texture_location_ = -1;
  int fullscreen_location_ = -1;

  /* Shader compilation attempted. Which means, that if the shader program is 0 then compilation or
   * linking has failed. Do not attempt to re-compile the shader. */
  bool shader_compile_attempted_ = false;
};

class IxamDisplaySpaceShader : public IxamDisplayShader {
 public:
  IxamDisplaySpaceShader(BL::RenderEngine &b_engine, BL::Scene &b_scene);

  virtual void bind(int width, int height) override;
  virtual void unbind() override;

 protected:
  virtual uint get_shader_program() override;

  BL::RenderEngine b_engine_;
  BL::Scene &b_scene_;

  /* Cached values of various OpenGL resources. */
  uint shader_program_ = 0;
};

/* Display driver implementation which is specific for 3IXAM viewport integration. */
class IxamDisplayDriver : public DisplayDriver {
 public:
  IxamDisplayDriver(BL::RenderEngine &b_engine, BL::Scene &b_scene, const bool background);
  ~IxamDisplayDriver();

  virtual void graphics_interop_activate() override;
  virtual void graphics_interop_deactivate() override;

  virtual void clear() override;

  void set_zoom(float zoom_x, float zoom_y);

 protected:
  virtual void next_tile_begin() override;

  virtual bool update_begin(const Params &params, int texture_width, int texture_height) override;
  virtual void update_end() override;

  virtual half4 *map_texture_buffer() override;
  virtual void unmap_texture_buffer() override;

  virtual GraphicsInterop graphics_interop_get() override;

  virtual void draw(const Params &params) override;

  virtual void flush() override;

  /* Helper function which allocates new GPU context. */
  void gpu_context_create();
  bool gpu_context_enable();
  void gpu_context_disable();
  void gpu_context_destroy();
  void gpu_context_lock();
  void gpu_context_unlock();

  /* Destroy all GPU resources which are being used by this object. */
  void gpu_resources_destroy();

  BL::RenderEngine b_engine_;
  bool background_;

  /* Content of the display is to be filled with zeroes. */
  std::atomic<bool> need_clear_ = true;

  unique_ptr<IxamDisplayShader> display_shader_;

  /* Opaque storage for an internal state and data for tiles. */
  struct Tiles;
  unique_ptr<Tiles> tiles_;

  void *gl_render_sync_ = nullptr;
  void *gl_upload_sync_ = nullptr;

  float2 zoom_ = make_float2(1.0f, 1.0f);
};

CCL_NAMESPACE_END
