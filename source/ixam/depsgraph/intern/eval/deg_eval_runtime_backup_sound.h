

/** \file
 * \ingroup depsgraph
 */

#pragma once

struct bSound;

namespace ixam::deg {

struct Depsgraph;

/* Backup of sound datablocks runtime data. */
class SoundBackup {
 public:
  SoundBackup(const Depsgraph *depsgraph);

  void reset();

  void init_from_sound(bSound *sound);
  void restore_to_sound(bSound *sound);

  void *cache;
  void *waveform;
  void *playback_handle;
};

}  // namespace ixam::deg
