

#pragma once

#include "tree_element.hh"

struct Scene;

namespace ixam::ed::outliner {

class TreeElementSceneObjectsBase final : public AbstractTreeElement {
  Scene &scene_;

 public:
  TreeElementSceneObjectsBase(TreeElement &legacy_te, Scene &scene);

  void expand(SpaceOutliner &) const override;
};

}  // namespace ixam::ed::outliner
