

/** \file
 * \ingroup depsgraph
 */

#pragma once

#include "BKE_modifier.h"

struct ModifierData;

namespace ixam::deg {

class ModifierDataBackup {
 public:
  explicit ModifierDataBackup(ModifierData *modifier_data);

  ModifierType type;
  void *runtime;
};

}  // namespace ixam::deg
