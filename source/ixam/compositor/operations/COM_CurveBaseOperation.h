

#pragma once

#include "COM_MultiThreadedOperation.h"

struct CurveMapping;

namespace ixam::compositor {

class CurveBaseOperation : public MultiThreadedOperation {
 protected:
  /**
   * Cached reference to the input_program
   */
  CurveMapping *curve_mapping_;

 public:
  CurveBaseOperation();
  ~CurveBaseOperation();

  /**
   * Initialize the execution
   */
  void init_execution() override;
  void deinit_execution() override;

  void set_curve_mapping(const CurveMapping *mapping);
};

}  // namespace ixam::compositor
