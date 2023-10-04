
set(INC
  .
  ..
  ../..
  ../../../makesdna
  ../../../../../intern/atomic
  ../../../../../intern/guardedalloc
)

include_directories(${INC})

ixam_test_performance(BLI_ghash_performance "bf_ixamlib")
ixam_test_performance(BLI_task_performance "bf_ixamlib")
