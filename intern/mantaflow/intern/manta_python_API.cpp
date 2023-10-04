

/** \file
 * \ingroup intern_mantaflow
 */

#include "manta_python_API.h"
#include "manta.h"

PyObject *Manta_initPython(void)
{
  return Pb::PyInit_manta_main();
}
