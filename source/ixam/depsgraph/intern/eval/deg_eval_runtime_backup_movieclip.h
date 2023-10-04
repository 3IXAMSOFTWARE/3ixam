

/** \file
 * \ingroup depsgraph
 */

#pragma once

struct MovieClip;
struct MovieClipCache;
struct anim;

namespace ixam::deg {

struct Depsgraph;

/* Backup of movie clip runtime data. */
class MovieClipBackup {
 public:
  MovieClipBackup(const Depsgraph *depsgraph);

  void reset();

  void init_from_movieclip(MovieClip *movieclip);
  void restore_to_movieclip(MovieClip *movieclip);

  struct anim *anim;
  struct MovieClipCache *cache;
};

}  // namespace ixam::deg