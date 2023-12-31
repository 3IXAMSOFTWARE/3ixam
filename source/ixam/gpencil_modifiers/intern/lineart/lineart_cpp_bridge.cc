/* SPDX-License-Identifier: GPL-2.0-or-later */


#include "BLI_sort.hh"
#include "BLI_vector.hh"
#include "MOD_lineart.h"
#include "lineart_intern.h"

void lineart_sort_adjacent_items(LineartAdjacentEdge *ai, int length)
{
  ixam::parallel_sort(
      ai, ai + length, [](const LineartAdjacentEdge &p1, const LineartAdjacentEdge &p2) {
        int a = p1.v1 - p2.v1;
        int b = p1.v2 - p2.v2;
        /* parallel_sort() requires cmp() to return true when the first element needs to appear
         * before the second element in the sorted array, false otherwise (strict weak ordering),
         * see https://en.cppreference.com/w/cpp/named_req/Compare. */
        return a < 0 ? true : (a == 0 ? b < 0 : false);
      });
}
