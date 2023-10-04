

#pragma once

#include "tree_element.hh"

namespace ixam::ed::outliner {

class TreeElementViewLayerBase final : public AbstractTreeElement {
  Scene &scene_;

 public:
  TreeElementViewLayerBase(TreeElement &legacy_te, Scene &scene);

  void expand(SpaceOutliner &) const override;
};

}  // namespace ixam::ed::outliner
