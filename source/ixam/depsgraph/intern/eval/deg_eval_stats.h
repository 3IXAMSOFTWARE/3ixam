

/** \file
 * \ingroup depsgraph
 */

#pragma once

namespace ixam::deg {

struct Depsgraph;

/* Aggregate operation timings to overall component and ID nodes timing. */
void deg_eval_stats_aggregate(Depsgraph *graph);

}  // namespace ixam::deg
