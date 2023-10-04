

#include "BLI_hash.hh"

#include "asset_library_reference.hh"

namespace ixam::ed::asset {

AssetLibraryReferenceWrapper::AssetLibraryReferenceWrapper(const AssetLibraryReference &reference)
    : AssetLibraryReference(reference)
{
}

bool operator==(const AssetLibraryReferenceWrapper &a, const AssetLibraryReferenceWrapper &b)
{
  return (a.type == b.type) &&
         ((a.type == ASSET_LIBRARY_CUSTOM) ? (a.custom_library_index == b.custom_library_index) :
                                             true);
}

uint64_t AssetLibraryReferenceWrapper::hash() const
{
  uint64_t hash1 = DefaultHash<decltype(type)>{}(type);
  if (type != ASSET_LIBRARY_CUSTOM) {
    return hash1;
  }

  uint64_t hash2 = DefaultHash<decltype(custom_library_index)>{}(custom_library_index);
  return hash1 ^ (hash2 * 33); /* Copied from DefaultHash for std::pair. */
}

}  // namespace ixam::ed::asset