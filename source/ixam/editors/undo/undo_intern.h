

#pragma once

/* internal exports only */

struct UndoType;

/* memfile_undo.c */

/** Export for ED_undo_sys. */
void ED_memfile_undosys_type(struct UndoType *ut);
