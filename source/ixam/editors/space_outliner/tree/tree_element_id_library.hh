

#pragma once

#include "tree_element_id.hh"

struct Library;

namespace ixam::ed::outliner {

class TreeElementIDLibrary final : public TreeElementID {
 public:
  TreeElementIDLibrary(TreeElement &legacy_te, Library &library);

  bool isExpandValid() const override;

  ixam::StringRefNull getWarning() const override;
};

}  // namespace ixam::ed::outliner
