

#pragma once

#include "COM_NodeOperation.h"

namespace ixam::compositor {

class SocketProxyOperation : public NodeOperation {
 public:
  SocketProxyOperation(DataType type, bool use_conversion);

  std::unique_ptr<MetaData> get_meta_data() override;
};

}  // namespace ixam::compositor
