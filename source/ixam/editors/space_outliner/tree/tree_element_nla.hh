

#pragma once

#include "tree_element.hh"

struct NlaTrack;

namespace ixam::ed::outliner {

class TreeElementNLA final : public AbstractTreeElement {
  AnimData &anim_data_;

 public:
  TreeElementNLA(TreeElement &legacy_te, AnimData &anim_data);

  void expand(SpaceOutliner &space_outliner) const override;
};

class TreeElementNLATrack final : public AbstractTreeElement {
  NlaTrack &track_;

 public:
  TreeElementNLATrack(TreeElement &legacy_te, NlaTrack &track);

  void expand(SpaceOutliner &space_outliner) const override;
};

class TreeElementNLAAction final : public AbstractTreeElement {
 public:
  TreeElementNLAAction(TreeElement &legacy_te, const bAction &action);
};

}  // namespace ixam::ed::outliner