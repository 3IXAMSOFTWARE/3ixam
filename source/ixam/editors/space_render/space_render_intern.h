/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * The Original Code is Copyright (C) 2008 Blender Foundation.
 * All rights reserved.
 */

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
