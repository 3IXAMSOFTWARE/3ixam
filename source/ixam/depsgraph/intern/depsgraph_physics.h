

/** \file
 * \ingroup depsgraph
 */

#pragma once

struct Collection;
struct ListBase;

namespace ixam::deg {

struct Depsgraph;

ListBase *build_effector_relations(Depsgraph *graph, Collection *collection);
ListBase *build_collision_relations(Depsgraph *graph,
                                    Collection *collection,
                                    unsigned int modifier_type);
void clear_physics_relations(Depsgraph *graph);

}  // namespace ixam::deg