# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright 2014 Blender Foundation. All rights reserved.

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
