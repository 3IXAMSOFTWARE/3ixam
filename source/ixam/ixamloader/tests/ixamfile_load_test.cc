
#include "ixamfile_loading_base_test.h"

class IxamfileLoadingTest : public IxamfileLoadingBaseTest {
};

TEST_F(IxamfileLoadingTest, CanaryTest)
{
  /* Load the smallest ixam file we have in the SVN lib/tests directory. */
  if (!ixamfile_load("modifier_stack/array_test.ixam")) {
    return;
  }
  depsgraph_create(DAG_EVAL_RENDER);
  EXPECT_NE(nullptr, this->depsgraph);
}
