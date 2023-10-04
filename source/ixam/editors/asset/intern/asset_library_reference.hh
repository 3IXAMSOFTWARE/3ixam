
/** \file
 * \ingroup edasset
 *
 * Utility to extend #AssetLibraryReference with C++ functionality (operators, hash function, etc).
 */

#pragma once

#include <cstdint>

#include "DNA_asset_types.h"

namespace ixam::ed::asset {

/**
 * Wrapper to add logic to the AssetLibraryReference DNA struct.
 */
class AssetLibraryReferenceWrapper : public AssetLibraryReference {
 public:
  /* Intentionally not `explicit`, allow implicit conversion for convenience. Might have to be
   * NOLINT */
  AssetLibraryReferenceWrapper(const AssetLibraryReference &reference);
  ~AssetLibraryReferenceWrapper() = default;

  friend bool operator==(const AssetLibraryReferenceWrapper &a,
                         const AssetLibraryReferenceWrapper &b);
  uint64_t hash() const;
};

}  // namespace ixam::ed::asset
