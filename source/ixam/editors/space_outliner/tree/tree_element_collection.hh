/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include "tree_element.hh"

namespace ixam::ed::outliner {

class TreeElementCollectionBase final : public AbstractTreeElement {
  Scene &scene_;

 public:
  TreeElementCollectionBase(TreeElement &legacy_te, Scene &scene);

  void expand(SpaceOutliner &) const override;
};

}  // namespace ixam::ed::outliner
