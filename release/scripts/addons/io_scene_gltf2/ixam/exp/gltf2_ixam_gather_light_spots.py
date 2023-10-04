# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Ixam-IO authors.

from typing import Optional
from io_scene_gltf2.io.com import gltf2_io_lights_punctual


def gather_light_spot(ixam_lamp, export_settings) -> Optional[gltf2_io_lights_punctual.LightSpot]:

    if not __filter_light_spot(ixam_lamp, export_settings):
        return None

    spot = gltf2_io_lights_punctual.LightSpot(
        inner_cone_angle=__gather_inner_cone_angle(ixam_lamp, export_settings),
        outer_cone_angle=__gather_outer_cone_angle(ixam_lamp, export_settings)
    )
    return spot


def __filter_light_spot(ixam_lamp, _) -> bool:
    if ixam_lamp.type != "SPOT":
        return False

    return True


def __gather_inner_cone_angle(ixam_lamp, _) -> Optional[float]:
    angle = ixam_lamp.spot_size * 0.5
    return angle - angle * ixam_lamp.spot_blend


def __gather_outer_cone_angle(ixam_lamp, _) -> Optional[float]:
    return ixam_lamp.spot_size * 0.5
