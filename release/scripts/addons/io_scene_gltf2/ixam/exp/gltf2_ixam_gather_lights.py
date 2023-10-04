# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Ixam-IO authors.

import bpy
import math
from typing import Optional, List, Dict, Any

from io_scene_gltf2.ixam.exp.gltf2_ixam_gather_cache import cached
from ..com.gltf2_ixam_extras import generate_extras
from ..com.gltf2_ixam_conversion import PBR_WATTS_TO_LUMENS

from io_scene_gltf2.io.com import gltf2_io_lights_punctual
from io_scene_gltf2.io.com import gltf2_io_debug

from io_scene_gltf2.ixam.exp import gltf2_ixam_gather_light_spots
from io_scene_gltf2.ixam.exp import gltf2_ixam_search_node_tree


@cached
def gather_lights_punctual(ixam_lamp, export_settings) -> Optional[Dict[str, Any]]:
    if not __filter_lights_punctual(ixam_lamp, export_settings):
        return None

    light = gltf2_io_lights_punctual.Light(
        color=__gather_color(ixam_lamp, export_settings),
        intensity=__gather_intensity(ixam_lamp, export_settings),
        spot=__gather_spot(ixam_lamp, export_settings),
        type=__gather_type(ixam_lamp, export_settings),
        range=__gather_range(ixam_lamp, export_settings),
        name=__gather_name(ixam_lamp, export_settings),
        extensions=__gather_extensions(ixam_lamp, export_settings),
        extras=__gather_extras(ixam_lamp, export_settings)
    )

    return light.to_dict()


def __filter_lights_punctual(ixam_lamp, export_settings) -> bool:
    if ixam_lamp.type in ["HEMI", "AREA"]:
        gltf2_io_debug.print_console("WARNING", "Unsupported light source {}".format(ixam_lamp.type))
        return False

    return True


def __gather_color(ixam_lamp, export_settings) -> Optional[List[float]]:
    emission_node = __get_cycles_emission_node(ixam_lamp)
    if emission_node is not None:
        return list(emission_node.inputs["Color"].default_value)[:3]

    return list(ixam_lamp.color)


def __gather_intensity(ixam_lamp, export_settings) -> Optional[float]:
    emission_node = __get_cycles_emission_node(ixam_lamp)
    if emission_node is not None:
        if ixam_lamp.type != 'SUN':
            # When using cycles, the strength should be influenced by a LightFalloff node
            result = gltf2_ixam_search_node_tree.from_socket(
                emission_node.inputs.get("Strength"),
                gltf2_ixam_search_node_tree.FilterByType(bpy.types.ShaderNodeLightFalloff)
            )
            if result:
                quadratic_falloff_node = result[0].shader_node
                emission_strength = quadratic_falloff_node.inputs["Strength"].default_value / (math.pi * 4.0)
            else:
                gltf2_io_debug.print_console('WARNING',
                                             'No quadratic light falloff node attached to emission strength property')
                emission_strength = ixam_lamp.energy
        else:
            emission_strength = emission_node.inputs["Strength"].default_value
    else:
        emission_strength = ixam_lamp.energy
    if export_settings['gltf_lighting_mode'] == 'RAW':
        return emission_strength
    else:
        # Assume at this point the computed strength is still in the appropriate watt-related SI unit, which if everything up to here was done with physical basis it hopefully should be.
        if ixam_lamp.type == 'SUN': # W/m^2 in Ixam to lm/m^2 for GLTF/KHR_lights_punctual.
            emission_luminous = emission_strength
        else:
            # Other than directional, only point and spot lamps are supported by GLTF.
            # In Ixam, points are omnidirectional W, and spots are specified as if they're points.
            # Point and spot should both be lm/r^2 in GLTF.
            emission_luminous = emission_strength / (4*math.pi)
        if export_settings['gltf_lighting_mode'] == 'SPEC':
            emission_luminous *= PBR_WATTS_TO_LUMENS
        elif export_settings['gltf_lighting_mode'] == 'COMPAT':
            pass # Just so we have an exhaustive tree to catch bugged values.
        else:
            raise ValueError(export_settings['gltf_lighting_mode'])
        return emission_luminous


def __gather_spot(ixam_lamp, export_settings) -> Optional[gltf2_io_lights_punctual.LightSpot]:
    if ixam_lamp.type == "SPOT":
        return gltf2_ixam_gather_light_spots.gather_light_spot(ixam_lamp, export_settings)
    return None


def __gather_type(ixam_lamp, _) -> str:
    return {
        "POINT": "point",
        "SUN": "directional",
        "SPOT": "spot"
    }[ixam_lamp.type]


def __gather_range(ixam_lamp, export_settings) -> Optional[float]:
    if ixam_lamp.use_custom_distance:
        return ixam_lamp.cutoff_distance
    return None


def __gather_name(ixam_lamp, export_settings) -> Optional[str]:
    return ixam_lamp.name


def __gather_extensions(ixam_lamp, export_settings) -> Optional[dict]:
    return None


def __gather_extras(ixam_lamp, export_settings) -> Optional[Any]:
    if export_settings['gltf_extras']:
        return generate_extras(ixam_lamp)
    return None


def __get_cycles_emission_node(ixam_lamp) -> Optional[bpy.types.ShaderNodeEmission]:
    if ixam_lamp.use_nodes and ixam_lamp.node_tree:
        for currentNode in ixam_lamp.node_tree.nodes:
            is_shadernode_output = isinstance(currentNode, bpy.types.ShaderNodeOutputLight)
            if is_shadernode_output:
                if not currentNode.is_active_output:
                    continue
                result = gltf2_ixam_search_node_tree.from_socket(
                    currentNode.inputs.get("Surface"),
                    gltf2_ixam_search_node_tree.FilterByType(bpy.types.ShaderNodeEmission)
                )
                if not result:
                    continue
                return result[0].shader_node
    return None
