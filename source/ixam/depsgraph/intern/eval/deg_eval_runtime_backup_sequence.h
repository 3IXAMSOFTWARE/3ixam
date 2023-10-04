

/** \file
 * \ingroup depsgraph
 */

#pragma once

#include "BLI_listbase.h"

struct Sequence;

namespace ixam::deg {

struct Depsgraph;

/* Backup of a single strip. */
class SequenceBackup {
 public:
  SequenceBackup(const Depsgraph *depsgraph);

  void reset();

  void init_from_sequence(Sequence *sequence);
  void restore_to_sequence(Sequence *sequence);

  bool isEmpty() const;

  void *scene_sound;
  ListBase anims;
};

}  // namespace ixam::deg
