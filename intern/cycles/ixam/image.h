/* SPDX-License-Identifier: Apache-2.0
 * Copyright 2011-2022 Blender Foundation */


#ifndef __IXAM_IMAGE_H__
#define __IXAM_IMAGE_H__

#include "RNA_ixam_cpp.h"

#include "scene/image.h"

CCL_NAMESPACE_BEGIN

class IxamImageLoader : public ImageLoader {
 public:
  IxamImageLoader(BL::Image b_image,
                     const int frame,
                     const int tile_number,
                     const bool is_preview_render);

  bool load_metadata(const ImageDeviceFeatures &features, ImageMetaData &metadata) override;
  bool load_pixels(const ImageMetaData &metadata,
                   void *pixels,
                   const size_t pixels_size,
                   const bool associate_alpha) override;
  string name() const override;
  bool equals(const ImageLoader &other) const override;

  int get_tile_number() const override;

  BL::Image b_image;
  int frame;
  int tile_number;
  bool free_cache;
};

class IxamPointDensityLoader : public ImageLoader {
 public:
  IxamPointDensityLoader(BL::Depsgraph depsgraph, BL::ShaderNodeTexPointDensity b_node);

  bool load_metadata(const ImageDeviceFeatures &features, ImageMetaData &metadata) override;
  bool load_pixels(const ImageMetaData &metadata,
                   void *pixels,
                   const size_t pixels_size,
                   const bool associate_alpha) override;
  string name() const override;
  bool equals(const ImageLoader &other) const override;

  BL::Depsgraph b_depsgraph;
  BL::ShaderNodeTexPointDensity b_node;
};

CCL_NAMESPACE_END

#endif /* __IXAM_IMAGE_H__ */
