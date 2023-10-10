/* SPDX-License-Identifier: GPL-2.0-or-later */

#include "BLI_color.hh"
#include "BLI_cpp_type_make.hh"
#include "BLI_float4x4.hh"
#include "BLI_math_vec_types.hh"

BLI_CPP_TYPE_MAKE(bool, bool, CPPTypeFlags::BasicType)

BLI_CPP_TYPE_MAKE(float, float, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(float2, ixam::float2, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(float3, ixam::float3, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(float4x4, ixam::float4x4, CPPTypeFlags::BasicType)

BLI_CPP_TYPE_MAKE(int8, int8_t, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(int16, int16_t, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(int32, int32_t, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(int64, int64_t, CPPTypeFlags::BasicType)

BLI_CPP_TYPE_MAKE(uint8, uint8_t, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(uint16, uint16_t, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(uint32, uint32_t, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(uint64, uint64_t, CPPTypeFlags::BasicType)

BLI_CPP_TYPE_MAKE(ColorGeometry4f, ixam::ColorGeometry4f, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(ColorGeometry4b, ixam::ColorGeometry4b, CPPTypeFlags::BasicType)

BLI_CPP_TYPE_MAKE(string, std::string, CPPTypeFlags::BasicType)
BLI_CPP_TYPE_MAKE(StringVector, ixam::Vector<std::string>, CPPTypeFlags::None)
