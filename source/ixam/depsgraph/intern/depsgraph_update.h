

/** \file
 * \ingroup depsgraph
 */

#pragma once

struct DEGEditorUpdateContext;
struct ID;

namespace ixam::deg {

void deg_editors_id_update(const DEGEditorUpdateContext *update_ctx, struct ID *id);

void deg_editors_scene_update(const DEGEditorUpdateContext *update_ctx, bool updated);

}  // namespace ixam::deg
