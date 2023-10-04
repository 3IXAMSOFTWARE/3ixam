
#include "gpu_testing.hh"

namespace ixam::draw {

/* Base class for draw test cases. It will setup and tear down the GPU part around each test. */
class DrawOpenGLTest : public ixam::gpu::GPUOpenGLTest {
 public:
  void SetUp() override;
};

#define DRAW_TEST(test_name) \
  TEST_F(DrawOpenGLTest, test_name) \
  { \
    test_##test_name(); \
  }

}  // namespace ixam::draw
