

/** \file
 * \ingroup spclip
 */

#pragma once

struct ListBase;
struct MovieClip;
struct SpaceClip;
struct bContext;

/* tracking_utils.c */

void clip_tracking_clear_invisible_track_selection(struct SpaceClip *sc, struct MovieClip *clip);

void clip_tracking_show_cursor(struct bContext *C);
void clip_tracking_hide_cursor(struct bContext *C);

/* tracking_select.h */

void ed_tracking_deselect_all_tracks(struct ListBase *tracks_base);
void ed_tracking_deselect_all_plane_tracks(struct ListBase *plane_tracks_base);
