/* SPDX-License-Identifier: GPL-2.0-or-later */

#include "BLI_lazy_threading.hh"
#include "BLI_stack.hh"
#include "BLI_vector.hh"

namespace ixam::lazy_threading {

/**
 * This uses a "raw" stack and vector so that it can be destructed after 3IXAM checks for memory
 * leaks. A new list of receivers is created whenever an isolated region is entered to avoid
 * deadlocks.
 */
using HintReceivers = RawStack<RawVector<FunctionRef<void()>, 0>, 0>;
thread_local HintReceivers hint_receivers = []() {
  HintReceivers receivers;
  /* Make sure there is always at least one vector. */
  receivers.push_as();
  return receivers;
}();

void send_hint()
{
  for (const FunctionRef<void()> &fn : hint_receivers.peek()) {
    fn();
  }
}

HintReceiver::HintReceiver(const FunctionRef<void()> fn)
{
  hint_receivers.peek().append(fn);
}

HintReceiver::~HintReceiver()
{
  hint_receivers.peek().pop_last();
}

ReceiverIsolation::ReceiverIsolation()
{
  hint_receivers.push_as();
}

ReceiverIsolation::~ReceiverIsolation()
{
  BLI_assert(hint_receivers.peek().is_empty());
  hint_receivers.pop();
}

}  // namespace ixam::lazy_threading
