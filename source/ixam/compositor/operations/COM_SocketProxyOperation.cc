

#include "COM_SocketProxyOperation.h"

namespace ixam::compositor {

SocketProxyOperation::SocketProxyOperation(DataType type, bool use_conversion)
{
  this->add_input_socket(type);
  this->add_output_socket(type);
  flags_.is_proxy_operation = true;
  flags_.use_datatype_conversion = use_conversion;
}

std::unique_ptr<MetaData> SocketProxyOperation::get_meta_data()
{
  return this->get_input_socket(0)->get_reader()->get_meta_data();
}

}  // namespace ixam::compositor
