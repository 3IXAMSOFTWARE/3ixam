/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include <string>

#include "BLI_function_ref.hh"

struct AssetHandle;
struct AssetLibraryReference;
struct FileDirEntry;
struct bContext;

std::string ED_assetlist_asset_filepath_get(const bContext *C,
                                            const AssetLibraryReference &library_reference,
                                            const AssetHandle &asset_handle);

/* Can return false to stop iterating. */
using AssetListIterFn = ixam::FunctionRef<bool(AssetHandle)>;
void ED_assetlist_iterate(const AssetLibraryReference &library_reference, AssetListIterFn fn);
