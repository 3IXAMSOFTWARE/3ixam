

#include "BLI_timeit.hh"

#include "IO_stl.h"
#include "stl_import.hh"

void STL_import(bContext *C, const struct STLImportParams *import_params)
{
  SCOPED_TIMER("STL Import");
  ixam::io::stl::importer_main(C, *import_params);
}
