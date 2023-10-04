

/** \file
 * \ingroup depsgraph
 */

#pragma once

#include "intern/depsgraph_type.h"

struct Main;

namespace ixam::deg {

struct Depsgraph;

void register_graph(Depsgraph *depsgraph);
void unregister_graph(Depsgraph *depsgraph);
Span<Depsgraph *> get_all_registered_graphs(Main *bmain);

}  // namespace ixam::deg
