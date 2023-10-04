

#include "openvdb_capi.h"
#include <openvdb/openvdb.h>

int OpenVDB_getVersionHex()
{
  return openvdb::OPENVDB_LIBRARY_VERSION;
}
