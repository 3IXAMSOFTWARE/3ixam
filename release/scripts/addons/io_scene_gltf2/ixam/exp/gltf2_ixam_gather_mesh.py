# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Ixam-IO authors.

import bpy
from typing import Optional, Dict, List, Any, Tuple
from .gltf2_ixam_export_keys import MORPH
from io_scene_gltf2.ixam.exp.gltf2_ixam_gather_cache import cached, cached_by_key
from io_scene_gltf2.io.com import gltf2_io
from io_scene_gltf2.ixam.exp import gltf2_ixam_gather_primitives
from ..com.gltf2_ixam_extras import generate_extras
from io_scene_gltf2.io.com.gltf2_io_debug import print_console
from io_scene_gltf2.io.exp.gltf2_io_user_extensions import export_user_extensions


def get_mesh_cache_key(ixam_mesh,
                ixam_object,
                vertex_groups,
                modifiers,
                skip_filter,
                materials,
                original_mesh,
                export_settings):
    # Use id of original mesh
    # Do not use bpy.types that can be unhashable
    # Do not use mesh name, that can be not unique (when linked)

    # If materials are not exported, no need to cache by material
    if export_settings['gltf_materials'] is None:
        mats = None
    else:
        mats = tuple(id(m) if m is not None else None for m in materials)

    # TODO check what is really needed for modifiers

    mesh_to_id_cache = ixam_mesh if original_mesh is None else original_mesh
    return (
        (id(mesh_to_id_cache),),
        (modifiers,),
        (skip_filter,),             #TODO to check if still needed
        mats
    )

@cached_by_key(key=get_mesh_cache_key)
def gather_mesh(ixam_mesh: bpy.types.Mesh,
                uuid_for_skined_data,
                vertex_groups: Optional[bpy.types.VertexGroups],
                modifiers: Optional[bpy.types.ObjectModifiers],
                skip_filter: bool,
                materials: Tuple[bpy.types.Material],
                original_mesh: bpy.types.Mesh,
                export_settings
                ) -> Optional[gltf2_io.Mesh]:
    if not skip_filter and not __filter_mesh(ixam_mesh, vertex_groups, modifiers, export_settings):
        return None

    mesh = gltf2_io.Mesh(
        extensions=__gather_extensions(ixam_mesh, vertex_groups, modifiers, export_settings),
        extras=__gather_extras(ixam_mesh, vertex_groups, modifiers, export_settings),
        name=__gather_name(ixam_mesh, vertex_groups, modifiers, export_settings),
        weights=__gather_weights(ixam_mesh, vertex_groups, modifiers, export_settings),
        primitives=__gather_primitives(ixam_mesh, uuid_for_skined_data, vertex_groups, modifiers, materials, export_settings),
    )

    if len(mesh.primitives) == 0:
        print_console("WARNING", "Mesh '{}' has no primitives and will be omitted.".format(mesh.name))
        return None

    ixam_object = None
    if uuid_for_skined_data:
        ixam_object = export_settings['vtree'].nodes[uuid_for_skined_data].ixam_object


    export_user_extensions('gather_mesh_hook',
                           export_settings,
                           mesh,
                           ixam_mesh,
                           ixam_object,
                           vertex_groups,
                           modifiers,
                           skip_filter,
                           materials)

    return mesh


def __filter_mesh(ixam_mesh: bpy.types.Mesh,
                  vertex_groups: Optional[bpy.types.VertexGroups],
                  modifiers: Optional[bpy.types.ObjectModifiers],
                  export_settings
                  ) -> bool:

    if ixam_mesh.users == 0:
        return False
    return True


def __gather_extensions(ixam_mesh: bpy.types.Mesh,
                        vertex_groups: Optional[bpy.types.VertexGroups],
                        modifiers: Optional[bpy.types.ObjectModifiers],
                        export_settings
                        ) -> Any:
    return None


def __gather_extras(ixam_mesh: bpy.types.Mesh,
                    vertex_groups: Optional[bpy.types.VertexGroups],
                    modifiers: Optional[bpy.types.ObjectModifiers],
                    export_settings
                    ) -> Optional[Dict[Any, Any]]:

    extras = {}

    if export_settings['gltf_extras']:
        extras = generate_extras(ixam_mesh) or {}

    if export_settings[MORPH] and ixam_mesh.shape_keys:
        morph_max = len(ixam_mesh.shape_keys.key_blocks) - 1
        if morph_max > 0:
            target_names = []
            for ixam_shape_key in ixam_mesh.shape_keys.key_blocks:
                if ixam_shape_key != ixam_shape_key.relative_key:
                    if ixam_shape_key.mute is False:
                        target_names.append(ixam_shape_key.name)
            extras['targetNames'] = target_names

    if extras:
        return extras

    return None


def __gather_name(ixam_mesh: bpy.types.Mesh,
                  vertex_groups: Optional[bpy.types.VertexGroups],
                  modifiers: Optional[bpy.types.ObjectModifiers],
                  export_settings
                  ) -> str:
    return ixam_mesh.name


def __gather_primitives(ixam_mesh: bpy.types.Mesh,
                        uuid_for_skined_data,
                        vertex_groups: Optional[bpy.types.VertexGroups],
                        modifiers: Optional[bpy.types.ObjectModifiers],
                        materials: Tuple[bpy.types.Material],
                        export_settings
                        ) -> List[gltf2_io.MeshPrimitive]:
    return gltf2_ixam_gather_primitives.gather_primitives(ixam_mesh,
                                                             uuid_for_skined_data,
                                                             vertex_groups,
                                                             modifiers,
                                                             materials,
                                                             export_settings)


def __gather_weights(ixam_mesh: bpy.types.Mesh,
                     vertex_groups: Optional[bpy.types.VertexGroups],
                     modifiers: Optional[bpy.types.ObjectModifiers],
                     export_settings
                     ) -> Optional[List[float]]:
    if not export_settings[MORPH] or not ixam_mesh.shape_keys:
        return None

    morph_max = len(ixam_mesh.shape_keys.key_blocks) - 1
    if morph_max <= 0:
        return None

    weights = []

    for ixam_shape_key in ixam_mesh.shape_keys.key_blocks:
        if ixam_shape_key != ixam_shape_key.relative_key:
            if ixam_shape_key.mute is False:
                weights.append(ixam_shape_key.value)

    return weights
