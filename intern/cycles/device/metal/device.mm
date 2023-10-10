/* SPDX-License-Identifier: Apache-2.0
 * Copyright 2021-2022 Blender Foundation */


#ifdef WITH_METAL

#  include "device/metal/device.h"
#  include "device/metal/device_impl.h"

#endif

#include "util/debug.h"
#include "util/set.h"
#include "util/system.h"

CCL_NAMESPACE_BEGIN

#ifdef WITH_METAL

Device *device_metal_create(const DeviceInfo &info, Stats &stats, Profiler &profiler)
{
  return new MetalDevice(info, stats, profiler);
}

bool device_metal_init()
{
  return true;
}

static int device_metal_get_num_devices_safe(uint32_t *num_devices)
{
  *num_devices = MTLCopyAllDevices().count;
  return 0;
}

void device_metal_info(vector<DeviceInfo> &devices)
{
  auto usable_devices = MetalInfo::get_usable_devices();
  /* Devices are numbered consecutively across platforms. */
  set<string> unique_ids;
  int device_index = 0;
  for (id<MTLDevice> &device : usable_devices) {
    /* Compute unique ID for persistent user preferences. */
    string device_name = MetalInfo::get_device_name(device);
    
    string id = string("METAL_") + device_name;
    
    /* Hardware ID might not be unique, add device number in that case. */
    if (unique_ids.find(id) != unique_ids.end()) {
      id += string_printf("_ID_%d", device_index);
    }
    unique_ids.insert(id);
    
    /* Create DeviceInfo. */
    DeviceInfo info;
    info.type = DEVICE_METAL;
    info.description = string_remove_trademark(string(device_name));
    
    info.num = device_index;
    /* We don't know if it's used for display, but assume it is. */
    info.display_device = true;
    info.denoisers = DENOISER_NONE;
    info.id = id;
    
    devices.push_back(info);
    device_index++;
  }
}

string device_metal_capabilities()
{
  string result = "";
  string error_msg = "";
  uint32_t num_devices = 0;
  if (num_devices == 0) {
    return "No Metal devices found\n";
  }
  result += string_printf("Number of devices: %u\n", num_devices);

  NSArray<id<MTLDevice>> *allDevices = MTLCopyAllDevices();
  for (id<MTLDevice> device in allDevices) {
    result += string_printf("\t\tDevice: %s\n", [device.name UTF8String]);
  }

  return result;
}

#else

Device *device_metal_create(const DeviceInfo &info, Stats &stats, Profiler &profiler)
{
  return nullptr;
}

bool device_metal_init()
{
  return false;
}

void device_metal_info(vector<DeviceInfo> &devices)
{
}

string device_metal_capabilities()
{
  return "";
}

#endif

CCL_NAMESPACE_END
