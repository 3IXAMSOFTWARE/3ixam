
#pragma once

#include "GHOST_NDOFManager.h"

class GHOST_NDOFManagerWin32 : public GHOST_NDOFManager {
 public:
  GHOST_NDOFManagerWin32(GHOST_System &);
  bool available();
};
