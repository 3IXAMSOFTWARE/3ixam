/* SPDX-License-Identifier: GPL-2.0-or-later */


#pragma once

#include "tree_element.hh"

namespace ixam::ed::outliner {

class TreeElementDriverBase final : public AbstractTreeElement {
  AnimData &anim_data_;

 public:
  TreeElementDriverBase(TreeElement &legacy_te, AnimData &anim_data);

  void expand(SpaceOutliner &space_outliner) const override;
};

}  // namespace ixam::ed::outliner
