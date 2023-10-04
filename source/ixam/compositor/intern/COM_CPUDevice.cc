

#include "COM_CPUDevice.h"

#include "COM_ExecutionGroup.h"
#include "COM_NodeOperation.h"

namespace ixam::compositor {

CPUDevice::CPUDevice(int thread_id) : thread_id_(thread_id)
{
}

void CPUDevice::execute(WorkPackage *work_package)
{
  switch (work_package->type) {
    case eWorkPackageType::Tile: {
      const uint chunk_number = work_package->chunk_number;
      ExecutionGroup *execution_group = work_package->execution_group;

      execution_group->get_output_operation()->execute_region(&work_package->rect, chunk_number);
      execution_group->finalize_chunk_execution(chunk_number, nullptr);
      break;
    }
    case eWorkPackageType::CustomFunction: {
      work_package->execute_fn();
      break;
    }
  }

  if (work_package->executed_fn) {
    work_package->executed_fn();
  }
}

}  // namespace ixam::compositor
