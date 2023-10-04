

#pragma once

#include "util/string.h"
#include "util/vector.h"

CCL_NAMESPACE_BEGIN

class Device;
class DeviceInfo;
class Profiler;
class Stats;

Device *device_dummy_create(const DeviceInfo &info, Stats &stats, Profiler &profiler);

CCL_NAMESPACE_END
