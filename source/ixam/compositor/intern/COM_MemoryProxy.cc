

#include "COM_MemoryProxy.h"
#include "COM_MemoryBuffer.h"

namespace ixam::compositor {

MemoryProxy::MemoryProxy(DataType datatype)
{
  write_buffer_operation_ = nullptr;
  executor_ = nullptr;
  buffer_ = nullptr;
  datatype_ = datatype;
}

void MemoryProxy::allocate(uint width, uint height)
{
  rcti result;
  result.xmin = 0;
  result.xmax = width;
  result.ymin = 0;
  result.ymax = height;

  buffer_ = new MemoryBuffer(this, result, MemoryBufferState::Default);
}

void MemoryProxy::free()
{
  if (buffer_) {
    delete buffer_;
    buffer_ = nullptr;
  }
}

}  // namespace ixam::compositor
