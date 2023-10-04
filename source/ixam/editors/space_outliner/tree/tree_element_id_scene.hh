

#pragma once

#include "tree_element_id.hh"

namespace ixam::ed::outliner {

class TreeElementIDScene final : public TreeElementID {
  Scene &scene_;

 public:
  TreeElementIDScene(TreeElement &legacy_te, Scene &scene);

  void expand(SpaceOutliner &) const override;
  bool isExpandValid() const override;

 private:
  void expandViewLayers(SpaceOutliner &) const;
  void expandWorld(SpaceOutliner &) const;
  void expandCollections(SpaceOutliner &) const;
  void expandObjects(SpaceOutliner &) const;
};

}  // namespace ixam::ed::outliner
