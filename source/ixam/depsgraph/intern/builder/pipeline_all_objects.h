

/** \file
 * \ingroup depsgraph
 */

#pragma once

#include "pipeline_view_layer.h"

namespace ixam::deg {

/* Builds a dependency graph that contains all objects in the view layer.
 * This is contrary to the regular ViewLayerBuilderPipeline, which is limited to visible objects
 * (and their dependencies). */
class AllObjectsBuilderPipeline : public ViewLayerBuilderPipeline {
 public:
  AllObjectsBuilderPipeline(::Depsgraph *graph);

 protected:
  virtual unique_ptr<DepsgraphNodeBuilder> construct_node_builder() override;
  virtual unique_ptr<DepsgraphRelationBuilder> construct_relation_builder() override;
};

}  // namespace ixam::deg
