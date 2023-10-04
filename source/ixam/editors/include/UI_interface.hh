

#pragma once

#include <memory>

#include "BLI_string_ref.hh"
#include "BLI_vector.hh"

#include "UI_resources.h"

namespace ixam::nodes::geo_eval_log {
struct GeometryAttributeInfo;
}

struct StructRNA;
struct uiBlock;
struct uiSearchItems;

namespace ixam::ui {

class AbstractGridView;
class AbstractTreeView;

/**
 * An item in a breadcrumb-like context. Currently this struct is very simple, but more
 * could be added to it in the future, to support interactivity or tooltips, for example.
 */
struct ContextPathItem {
  /* Text to display in the UI. */
  std::string name;
  /* #BIFIconID */
  int icon;
  int icon_indicator_number;
};

void context_path_add_generic(Vector<ContextPathItem> &path,
                              StructRNA &rna_type,
                              void *ptr,
                              const BIFIconID icon_override = ICON_NONE);

void template_breadcrumbs(uiLayout &layout, Span<ContextPathItem> context_path);

void attribute_search_add_items(StringRefNull str,
                                bool can_create_attribute,
                                Span<const nodes::geo_eval_log::GeometryAttributeInfo *> infos,
                                uiSearchItems *items,
                                bool is_first);

}  // namespace ixam::ui

/**
 * Override this for all available view types.
 */
ixam::ui::AbstractGridView *UI_block_add_view(
    uiBlock &block,
    ixam::StringRef idname,
    std::unique_ptr<ixam::ui::AbstractGridView> grid_view);
ixam::ui::AbstractTreeView *UI_block_add_view(
    uiBlock &block,
    ixam::StringRef idname,
    std::unique_ptr<ixam::ui::AbstractTreeView> tree_view);
