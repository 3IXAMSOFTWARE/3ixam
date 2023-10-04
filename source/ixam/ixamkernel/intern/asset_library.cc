

#include <memory>

#include "BKE_asset_library.hh"
#include "BKE_main.h"
#include "BKE_preferences.h"

#include "BLI_fileops.h"
#include "BLI_path_util.h"

#include "DNA_asset_types.h"
#include "DNA_userdef_types.h"

#include "asset_library_service.hh"

bool ixam::bke::AssetLibrary::save_catalogs_when_file_is_saved = true;

ixam::bke::AssetLibrary *BKE_asset_library_load(const Main *bmain,
                                                   const AssetLibraryReference &library_reference)
{
  ixam::bke::AssetLibraryService *service = ixam::bke::AssetLibraryService::get();
  return service->get_asset_library(bmain, library_reference);
}

/**
 * Loading an asset library at this point only means loading the catalogs. Later on this should
 * invoke reading of asset representations too.
 */
struct AssetLibrary *BKE_asset_library_load(const char *library_path)
{
  ixam::bke::AssetLibraryService *service = ixam::bke::AssetLibraryService::get();
  ixam::bke::AssetLibrary *lib;
  if (library_path == nullptr || library_path[0] == '\0') {
    lib = service->get_asset_library_current_file();
  }
  else {
    lib = service->get_asset_library_on_disk(library_path);
  }
  return reinterpret_cast<struct AssetLibrary *>(lib);
}

bool BKE_asset_library_has_any_unsaved_catalogs()
{
  ixam::bke::AssetLibraryService *service = ixam::bke::AssetLibraryService::get();
  return service->has_any_unsaved_catalogs();
}

bool BKE_asset_library_find_suitable_root_path_from_path(const char *input_path,
                                                         char *r_library_path)
{
  if (bUserAssetLibrary *preferences_lib = BKE_preferences_asset_library_containing_path(
          &U, input_path)) {
    BLI_strncpy(r_library_path, preferences_lib->path, FILE_MAXDIR);
    return true;
  }

  BLI_split_dir_part(input_path, r_library_path, FILE_MAXDIR);
  return r_library_path[0] != '\0';
}

bool BKE_asset_library_find_suitable_root_path_from_main(const Main *bmain, char *r_library_path)
{
  return BKE_asset_library_find_suitable_root_path_from_path(bmain->filepath, r_library_path);
}

ixam::bke::AssetCatalogService *BKE_asset_library_get_catalog_service(
    const ::AssetLibrary *library_c)
{
  if (library_c == nullptr) {
    return nullptr;
  }

  const ixam::bke::AssetLibrary &library = reinterpret_cast<const ixam::bke::AssetLibrary &>(
      *library_c);
  return library.catalog_service.get();
}

ixam::bke::AssetCatalogTree *BKE_asset_library_get_catalog_tree(const ::AssetLibrary *library)
{
  ixam::bke::AssetCatalogService *catalog_service = BKE_asset_library_get_catalog_service(
      library);
  if (catalog_service == nullptr) {
    return nullptr;
  }

  return catalog_service->get_catalog_tree();
}

void BKE_asset_library_refresh_catalog_simplename(struct AssetLibrary *asset_library,
                                                  struct AssetMetaData *asset_data)
{
  ixam::bke::AssetLibrary *lib = reinterpret_cast<ixam::bke::AssetLibrary *>(asset_library);
  lib->refresh_catalog_simplename(asset_data);
}

namespace ixam::bke {

AssetLibrary::AssetLibrary() : catalog_service(std::make_unique<AssetCatalogService>())
{
}

AssetLibrary::~AssetLibrary()
{
  if (on_save_callback_store_.func) {
    on_ixam_save_handler_unregister();
  }
}

void AssetLibrary::load(StringRefNull library_root_directory)
{
  auto catalog_service = std::make_unique<AssetCatalogService>(library_root_directory);
  catalog_service->load_from_disk();
  this->catalog_service = std::move(catalog_service);
}

void AssetLibrary::refresh()
{
  this->catalog_service->reload_catalogs();
}

namespace {
void asset_library_on_save_post(struct Main *main,
                                struct PointerRNA **pointers,
                                const int num_pointers,
                                void *arg)
{
  AssetLibrary *asset_lib = static_cast<AssetLibrary *>(arg);
  asset_lib->on_ixam_save_post(main, pointers, num_pointers);
}

}  // namespace

void AssetLibrary::on_ixam_save_handler_register()
{
  /* The callback system doesn't own `on_save_callback_store_`. */
  on_save_callback_store_.alloc = false;

  on_save_callback_store_.func = asset_library_on_save_post;
  on_save_callback_store_.arg = this;

  BKE_callback_add(&on_save_callback_store_, BKE_CB_EVT_SAVE_POST);
}

void AssetLibrary::on_ixam_save_handler_unregister()
{
  BKE_callback_remove(&on_save_callback_store_, BKE_CB_EVT_SAVE_POST);
  on_save_callback_store_.func = nullptr;
  on_save_callback_store_.arg = nullptr;
}

void AssetLibrary::on_ixam_save_post(struct Main *main,
                                      struct PointerRNA ** /*pointers*/,
                                      const int /*num_pointers*/)
{
  if (this->catalog_service == nullptr) {
    return;
  }

  if (save_catalogs_when_file_is_saved) {
    this->catalog_service->write_to_disk(main->filepath);
  }
}

void AssetLibrary::refresh_catalog_simplename(struct AssetMetaData *asset_data)
{
  if (BLI_uuid_is_nil(asset_data->catalog_id)) {
    asset_data->catalog_simple_name[0] = '\0';
    return;
  }
  const AssetCatalog *catalog = this->catalog_service->find_catalog(asset_data->catalog_id);
  if (catalog == nullptr) {
    /* No-op if the catalog cannot be found. This could be the kind of "the catalog definition file
     * is corrupt/lost" scenario that the simple name is meant to help recover from. */
    return;
  }
  STRNCPY(asset_data->catalog_simple_name, catalog->simple_name.c_str());
}

Vector<AssetLibraryReference> all_valid_asset_library_refs()
{
  Vector<AssetLibraryReference> result;
  int i;
  LISTBASE_FOREACH_INDEX (const bUserAssetLibrary *, asset_library, &U.asset_libraries, i) {
    if (!BLI_is_dir(asset_library->path)) {
      continue;
    }
    AssetLibraryReference library_ref{};
    library_ref.custom_library_index = i;
    library_ref.type = ASSET_LIBRARY_CUSTOM;
    result.append(library_ref);
  }

  AssetLibraryReference library_ref{};
  library_ref.custom_library_index = -1;
  library_ref.type = ASSET_LIBRARY_LOCAL;
  result.append(library_ref);
  return result;
}

}  // namespace ixam::bke
