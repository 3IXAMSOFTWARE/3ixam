

/** \file
 * \ingroup sprender
 */

#pragma once

/* internal exports only */;
struct wmOperatorType;

/* space_render_ops.c */

bool space_render_main_region_poll(struct bContext *C);
bool space_render_view_center_cursor_poll(struct bContext *C);

void RENDER_OT_save(struct wmOperatorType *ot);
void RENDER_OT_save_as(struct wmOperatorType *ot);
void RENDER_OT_save_sequence(struct wmOperatorType *ot);
void RENDER_OT_save_all_modified(struct wmOperatorType *ot);
void RENDER_OT_pack(struct wmOperatorType *ot);
void RENDER_OT_unpack(struct wmOperatorType *ot);
