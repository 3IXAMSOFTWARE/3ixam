

#pragma once

/** \file
 * \ingroup editor/io
 */

struct wmOperatorType;

void CACHEFILE_OT_open(struct wmOperatorType *ot);
void CACHEFILE_OT_reload(struct wmOperatorType *ot);

void CACHEFILE_OT_layer_add(struct wmOperatorType *ot);
void CACHEFILE_OT_layer_remove(struct wmOperatorType *ot);
void CACHEFILE_OT_layer_move(struct wmOperatorType *ot);
