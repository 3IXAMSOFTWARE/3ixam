

#pragma once

#ifndef __cplusplus
#  error This is a C++-only header file.
#endif

#include "BKE_asset_library.hh"

#include "BLI_map.hh"

#include <memory>

namespace ixam::bke {

/**
 * Global singleton-ish that provides access to individual #AssetLibrary instances.
 *
 * Whenever a ixam file is loaded, the existing instance of AssetLibraryService is destructed, and
 * a new one is created -- hence the "singleton-ish". This ensures only information about relevant
 * asset libraries is loaded.
 *
 * \note How Asset libraries are identified may change in the future.
 *  For now they are assumed to be:
 * - on disk (identified by the absolute directory), or
 * - the "current file" library (which is in memory but could have catalogs
 *   loaded from a file on disk).
 */
class AssetLibraryService {
 public:
  using AssetLibraryPtr = std::unique_ptr<AssetLibrary>;

  AssetLibraryService() = default;
  ~AssetLibraryService() = default;

  /** Return the AssetLibraryService singleton, allocating it if necessary. */
  static AssetLibraryService *get();

  /** Destroy the AssetLibraryService singleton. It will be reallocated by #get() if necessary. */
  static void destroy();

  AssetLibrary *get_asset_library(const Main *bmain,
                                  const AssetLibraryReference &library_reference);

  /**
   * Get the given asset library. Opens it (i.e. creates a new AssetLibrary instance) if necessary.
   */
  AssetLibrary *get_asset_library_on_disk(StringRefNull top_level_directory);

  /** Get the "Current File" asset library. */
  AssetLibrary *get_asset_library_current_file();

  /** Returns whether there are any known asset libraries with unsaved catalog edits. */
  bool has_any_unsaved_catalogs() const;

 protected:
  static std::unique_ptr<AssetLibraryService> instance_;

  /* Mapping absolute path of the library's top-level directory to the AssetLibrary instance. */
  Map<std::string, AssetLibraryPtr> on_disk_libraries_;
  AssetLibraryPtr current_file_library_;

  /* Handlers for managing the life cycle of the AssetLibraryService instance. */
  bCallbackFuncStore on_load_callback_store_;
  static bool atexit_handler_registered_;

  /** Allocate a new instance of the service and assign it to `instance_`. */
  static void allocate_service_instance();

  /**
   * Ensure the AssetLibraryService instance is destroyed before a new ixam file is loaded.
   * This makes memory management simple, and ensures a fresh start for every ixam file. */
  void app_handler_register();
  void app_handler_unregister();
};

}  // namespace ixam::bke