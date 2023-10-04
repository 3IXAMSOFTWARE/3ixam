

#pragma once

#include "tree_element.hh"

struct bGPDlayer;

namespace ixam::ed::outliner {

class TreeElementGPencilLayer final : public AbstractTreeElement {
 public:
  TreeElementGPencilLayer(TreeElement &legacy_te, bGPDlayer &gplayer);
};

}  // namespace ixam::ed::outliner
