
#pragma once

/** \file
 * \ingroup bgpencil
 */
#include "gpencil_io_base.hh"

namespace ixam::io::gpencil {

class GpencilExporter : public GpencilIO {

 public:
  GpencilExporter(const struct GpencilIOParams *iparams) : GpencilIO(iparams){};
  virtual bool write() = 0;

 protected:
 private:
};

}  // namespace ixam::io::gpencil
