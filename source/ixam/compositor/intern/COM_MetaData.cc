/* SPDX-License-Identifier: GPL-2.0-or-later
 * Copyright 2021 Blender Foundation. */


#include "COM_MetaData.h"

#include "BKE_image.h"

#include "RE_pipeline.h"

namespace ixam::compositor {

void MetaData::add(const ixam::StringRef key, const ixam::StringRef value)
{
  entries_.add(key, value);
}

void MetaData::add_cryptomatte_entry(const ixam::StringRef layer_name,
                                     const ixam::StringRefNull key,
                                     const ixam::StringRef value)
{
  add(ixam::bke::cryptomatte::BKE_cryptomatte_meta_data_key(layer_name, key), value);
}

void MetaData::replace_hash_neutral_cryptomatte_keys(const ixam::StringRef layer_name)
{
  std::string cryptomatte_hash = entries_.pop_default(META_DATA_KEY_CRYPTOMATTE_HASH, "");
  std::string cryptomatte_conversion = entries_.pop_default(META_DATA_KEY_CRYPTOMATTE_CONVERSION,
                                                            "");
  std::string cryptomatte_manifest = entries_.pop_default(META_DATA_KEY_CRYPTOMATTE_MANIFEST, "");

  if (cryptomatte_hash.length() || cryptomatte_conversion.length() ||
      cryptomatte_manifest.length()) {
    add_cryptomatte_entry(layer_name, "name", layer_name);
  }
  if (cryptomatte_hash.length()) {
    add_cryptomatte_entry(layer_name, "hash", cryptomatte_hash);
  }
  if (cryptomatte_conversion.length()) {
    add_cryptomatte_entry(layer_name, "conversion", cryptomatte_conversion);
  }
  if (cryptomatte_manifest.length()) {
    add_cryptomatte_entry(layer_name, "manifest", cryptomatte_manifest);
  }
}

void MetaData::add_to_render_result(RenderResult *render_result) const
{
  for (Map<std::string, std::string>::Item entry : entries_.items()) {
    BKE_render_result_stamp_data(render_result, entry.key.c_str(), entry.value.c_str());
  }
}

void MetaDataExtractCallbackData::add_meta_data(ixam::StringRef key,
                                                ixam::StringRefNull value)
{
  if (!meta_data) {
    meta_data = std::make_unique<MetaData>();
  }
  meta_data->add(key, value);
}

void MetaDataExtractCallbackData::set_cryptomatte_keys(ixam::StringRef cryptomatte_layer_name)
{
  manifest_key = ixam::bke::cryptomatte::BKE_cryptomatte_meta_data_key(cryptomatte_layer_name,
                                                                          "manifest");
  hash_key = ixam::bke::cryptomatte::BKE_cryptomatte_meta_data_key(cryptomatte_layer_name,
                                                                      "hash");
  conversion_key = ixam::bke::cryptomatte::BKE_cryptomatte_meta_data_key(cryptomatte_layer_name,
                                                                            "conversion");
}

void MetaDataExtractCallbackData::extract_cryptomatte_meta_data(void *_data,
                                                                const char *propname,
                                                                char *propvalue,
                                                                int /*len*/)
{
  MetaDataExtractCallbackData *data = static_cast<MetaDataExtractCallbackData *>(_data);
  ixam::StringRefNull key(propname);
  if (key == data->hash_key) {
    data->add_meta_data(META_DATA_KEY_CRYPTOMATTE_HASH, propvalue);
  }
  else if (key == data->conversion_key) {
    data->add_meta_data(META_DATA_KEY_CRYPTOMATTE_CONVERSION, propvalue);
  }
  else if (key == data->manifest_key) {
    data->add_meta_data(META_DATA_KEY_CRYPTOMATTE_MANIFEST, propvalue);
  }
}

}  // namespace ixam::compositor
