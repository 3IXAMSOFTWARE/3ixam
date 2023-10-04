# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Ixam-IO authors.

import bpy
import typing

from io_scene_gltf2.io.com import gltf2_io
from io_scene_gltf2.ixam.exp import gltf2_ixam_gather_animation_channels
from io_scene_gltf2.io.com.gltf2_io_debug import print_console
from ..com.gltf2_ixam_extras import generate_extras
from io_scene_gltf2.io.exp.gltf2_io_user_extensions import export_user_extensions
from io_scene_gltf2.ixam.exp.gltf2_ixam_gather_tree import VExportNode
from ..com.gltf2_ixam_data_path import is_bone_anim_channel
from mathutils import Matrix


def gather_animations(  obj_uuid: int,
                        tracks: typing.Dict[str, typing.List[int]],
                        offset: int,
                        export_settings) -> typing.Tuple[typing.List[gltf2_io.Animation], typing.Dict[str, typing.List[int]]]:
    """
    Gather all animations which contribute to the objects property, and corresponding track names

    :param ixam_object: The ixam object which is animated
    :param export_settings:
    :return: A list of glTF2 animations and tracks
    """
    animations = []

    ixam_object = export_settings['vtree'].nodes[obj_uuid].ixam_object

    # Collect all 'actions' affecting this object. There is a direct mapping between ixam actions and glTF animations
    ixam_actions = __get_ixam_actions(ixam_object, export_settings)

    if len([a for a in ixam_actions if a[2] == "OBJECT"]) == 0:
        # No TRS animation are found for this object.
        # But we need to bake, in case we export selection
        # (Only when force sampling is ON)
        # If force sampling is OFF, can lead to inconsistent export anyway
        if export_settings['gltf_selected'] is True and ixam_object.type != "ARMATURE" and export_settings['gltf_force_sampling'] is True:
            # We also have to check if this is a skinned mesh, because we don't have to force animation baking on this case
            # (skinned meshes TRS must be ignored, says glTF specification)
            if export_settings['vtree'].nodes[obj_uuid].skin is None:
                channels = gltf2_ixam_gather_animation_channels.gather_channels_baked(obj_uuid, None, export_settings)
                if channels is not None:
                    animation = gltf2_io.Animation(
                            channels=channels,
                            extensions=None, # as other animations
                            extras=None, # Because there is no animation to get extras from
                            name=ixam_object.name, # Use object name as animation name
                            samplers=[]
                        )

                    __link_samplers(animation, export_settings)
                    if animation is not None:
                        animations.append(animation)
        elif export_settings['gltf_selected'] is True and ixam_object.type == "ARMATURE":
            # We need to bake all bones. Because some bone can have some constraints linking to
            # some other armature bones, for example
            #TODO
            pass


    current_action = None
    current_world_matrix = None
    if ixam_object.animation_data and ixam_object.animation_data.action:
        # There is an active action. Storing it, to be able to restore after switching all actions during export
        current_action = ixam_object.animation_data.action
    elif len(ixam_actions) != 0 and ixam_object.animation_data is not None and ixam_object.animation_data.action is None:
        # No current action set, storing world matrix of object
        current_world_matrix = ixam_object.matrix_world.copy()

    # Remove any solo (starred) NLA track. Restored after export
    solo_track = None
    if ixam_object.animation_data:
        for track in ixam_object.animation_data.nla_tracks:
            if track.is_solo:
                solo_track = track
                track.is_solo = False
                break

    # Remove any tweak mode. Restore after export
    if ixam_object.animation_data:
        restore_tweak_mode = ixam_object.animation_data.use_tweak_mode

    # Remove use of NLA. Restore after export
    if ixam_object.animation_data:
        current_use_nla = ixam_object.animation_data.use_nla
        ixam_object.animation_data.use_nla = False

    export_user_extensions('animation_switch_loop_hook', export_settings, ixam_object, False)

    # Export all collected actions.
    for ixam_action, track_name, on_type in ixam_actions:

        # Set action as active, to be able to bake if needed
        if on_type == "OBJECT": # Not for shapekeys!
            if ixam_object.animation_data.action is None \
                    or (ixam_object.animation_data.action.name != ixam_action.name):
                if ixam_object.animation_data.is_property_readonly('action'):
                    ixam_object.animation_data.use_tweak_mode = False
                try:
                    __reset_bone_matrix(ixam_object, export_settings)
                    export_user_extensions('pre_animation_switch_hook', export_settings, ixam_object, ixam_action, track_name, on_type)
                    ixam_object.animation_data.action = ixam_action
                    export_user_extensions('post_animation_switch_hook', export_settings, ixam_object, ixam_action, track_name, on_type)
                except:
                    error = "Action is readonly. Please check NLA editor"
                    print_console("WARNING", "Animation '{}' could not be exported. Cause: {}".format(ixam_action.name, error))
                    continue

        # No need to set active shapekeys animations, this is needed for bone baking

        animation = __gather_animation(obj_uuid, ixam_action, export_settings)
        if animation is not None:
            animations.append(animation)

            # Store data for merging animation later
            if track_name is not None: # Do not take into account animation not in NLA
                # Do not take into account default NLA track names
                if not (track_name.startswith("NlaTrack") or track_name.startswith("[Action Stash]")):
                    if track_name not in tracks.keys():
                        tracks[track_name] = []
                    tracks[track_name].append(offset + len(animations)-1) # Store index of animation in animations

    # Restore action status
    # TODO: do this in a finally
    if ixam_object.animation_data:
        if ixam_object.animation_data.action is not None:
            if current_action is None:
                # remove last exported action
                __reset_bone_matrix(ixam_object, export_settings)
                ixam_object.animation_data.action = None
            elif ixam_object.animation_data.action.name != current_action.name:
                # Restore action that was active at start of exporting
                __reset_bone_matrix(ixam_object, export_settings)
                ixam_object.animation_data.action = current_action
        if solo_track is not None:
            solo_track.is_solo = True
        ixam_object.animation_data.use_tweak_mode = restore_tweak_mode
        ixam_object.animation_data.use_nla = current_use_nla

    if current_world_matrix is not None:
        ixam_object.matrix_world = current_world_matrix

    export_user_extensions('animation_switch_loop_hook', export_settings, ixam_object, True)

    return animations, tracks


def __gather_animation( obj_uuid: int,
                        ixam_action: bpy.types.Action,
                        export_settings
                       ) -> typing.Optional[gltf2_io.Animation]:

    ixam_object = export_settings['vtree'].nodes[obj_uuid].ixam_object

    if not __filter_animation(ixam_action, ixam_object, export_settings):
        return None

    name = __gather_name(ixam_action, ixam_object, export_settings)
    try:
        animation = gltf2_io.Animation(
            channels=__gather_channels(obj_uuid, ixam_action, export_settings),
            extensions=__gather_extensions(ixam_action, ixam_object, export_settings),
            extras=__gather_extras(ixam_action, ixam_object, export_settings),
            name=name,
            samplers=__gather_samplers(obj_uuid, ixam_action, export_settings)
        )
    except RuntimeError as error:
        print_console("WARNING", "Animation '{}' could not be exported. Cause: {}".format(name, error))
        return None

    export_user_extensions('pre_gather_animation_hook', export_settings, animation, ixam_action, ixam_object)

    if not animation.channels:
        return None

    # To allow reuse of samplers in one animation,
    __link_samplers(animation, export_settings)

    export_user_extensions('gather_animation_hook', export_settings, animation, ixam_action, ixam_object)

    return animation


def __filter_animation(ixam_action: bpy.types.Action,
                       ixam_object: bpy.types.Object,
                       export_settings
                       ) -> bool:
    if ixam_action.users == 0:
        return False

    return True


def __gather_channels(obj_uuid: int,
                      ixam_action: bpy.types.Action,
                      export_settings
                      ) -> typing.List[gltf2_io.AnimationChannel]:
    return gltf2_ixam_gather_animation_channels.gather_animation_channels(
        obj_uuid, ixam_action, export_settings)


def __gather_extensions(ixam_action: bpy.types.Action,
                        ixam_object: bpy.types.Object,
                        export_settings
                        ) -> typing.Any:
    return None


def __gather_extras(ixam_action: bpy.types.Action,
                    ixam_object: bpy.types.Object,
                    export_settings
                    ) -> typing.Any:

    if export_settings['gltf_extras']:
        return generate_extras(ixam_action)
    return None


def __gather_name(ixam_action: bpy.types.Action,
                  ixam_object: bpy.types.Object,
                  export_settings
                  ) -> typing.Optional[str]:
    return ixam_action.name


def __gather_samplers(obj_uuid: str,
                      ixam_action: bpy.types.Action,
                      export_settings
                      ) -> typing.List[gltf2_io.AnimationSampler]:
    # We need to gather the samplers after gathering all channels --> populate this list in __link_samplers
    return []


def __link_samplers(animation: gltf2_io.Animation, export_settings):
    """
    Move animation samplers to their own list and store their indices at their previous locations.

    After gathering, samplers are stored in the channels properties of the animation and need to be moved
    to their own list while storing an index into this list at the position where they previously were.
    This behaviour is similar to that of the glTFExporter that traverses all nodes
    :param animation:
    :param export_settings:
    :return:
    """
    # TODO: move this to some util module and update gltf2 exporter also
    T = typing.TypeVar('T')

    def __append_unique_and_get_index(l: typing.List[T], item: T):
        if item in l:
            return l.index(item)
        else:
            index = len(l)
            l.append(item)
            return index

    for i, channel in enumerate(animation.channels):
        animation.channels[i].sampler = __append_unique_and_get_index(animation.samplers, channel.sampler)


def __get_ixam_actions(ixam_object: bpy.types.Object,
                            export_settings
                          ) -> typing.List[typing.Tuple[bpy.types.Action, str, str]]:
    ixam_actions = []
    ixam_tracks = {}
    action_on_type = {}

    export_user_extensions('pre_gather_actions_hook', export_settings, ixam_object)

    if ixam_object.animation_data is not None:
        # Collect active action.
        if ixam_object.animation_data.action is not None:
            ixam_actions.append(ixam_object.animation_data.action)
            ixam_tracks[ixam_object.animation_data.action.name] = None
            action_on_type[ixam_object.animation_data.action.name] = "OBJECT"

        # Collect associated strips from NLA tracks.
        if export_settings['gltf_nla_strips'] is True:
            for track in ixam_object.animation_data.nla_tracks:
                # Multi-strip tracks do not export correctly yet (they need to be baked),
                # so skip them for now and only write single-strip tracks.
                non_muted_strips = [strip for strip in track.strips if strip.action is not None and strip.mute is False]
                if track.strips is None or len(non_muted_strips) != 1:
                    continue
                for strip in non_muted_strips:
                    ixam_actions.append(strip.action)
                    ixam_tracks[strip.action.name] = track.name # Always set after possible active action -> None will be overwrite
                    action_on_type[strip.action.name] = "OBJECT"

    if ixam_object.type == "MESH" \
            and ixam_object.data is not None \
            and ixam_object.data.shape_keys is not None \
            and ixam_object.data.shape_keys.animation_data is not None:

            if ixam_object.data.shape_keys.animation_data.action is not None:
                ixam_actions.append(ixam_object.data.shape_keys.animation_data.action)
                ixam_tracks[ixam_object.data.shape_keys.animation_data.action.name] = None
                action_on_type[ixam_object.data.shape_keys.animation_data.action.name] = "SHAPEKEY"

            if export_settings['gltf_nla_strips'] is True:
                for track in ixam_object.data.shape_keys.animation_data.nla_tracks:
                    # Multi-strip tracks do not export correctly yet (they need to be baked),
                    # so skip them for now and only write single-strip tracks.
                    non_muted_strips = [strip for strip in track.strips if strip.action is not None and strip.mute is False]
                    if track.strips is None or len(non_muted_strips) != 1:
                        continue
                    for strip in non_muted_strips:
                        ixam_actions.append(strip.action)
                        ixam_tracks[strip.action.name] = track.name # Always set after possible active action -> None will be overwrite
                        action_on_type[strip.action.name] = "SHAPEKEY"

    # If there are only 1 armature, include all animations, even if not in NLA
    if export_settings['gltf_export_anim_single_armature'] is True:
        if ixam_object.type == "ARMATURE":
            if len(export_settings['vtree'].get_all_node_of_type(VExportNode.ARMATURE)) == 1:
                # Keep all actions on objects (no Shapekey animation)
                for act in [a for a in bpy.data.actions if a.id_root == "OBJECT"]:
                    # We need to check this is an armature action
                    # Checking that at least 1 bone is animated
                    if not __is_armature_action(act):
                        continue
                    # Check if this action is already taken into account
                    if act.name in ixam_tracks.keys():
                        continue
                    ixam_actions.append(act)
                    ixam_tracks[act.name] = None
                    action_on_type[act.name] = "OBJECT"

    # Use a class to get parameters, to be able to modify them
    class GatherActionHookParameters:
        def __init__(self, ixam_actions, ixam_tracks, action_on_type):
            self.ixam_actions = ixam_actions
            self.ixam_tracks = ixam_tracks
            self.action_on_type = action_on_type

    gatheractionhookparams = GatherActionHookParameters(ixam_actions, ixam_tracks, action_on_type)

    export_user_extensions('gather_actions_hook', export_settings, ixam_object, gatheractionhookparams)

    # Get params back from hooks
    ixam_actions = gatheractionhookparams.ixam_actions
    ixam_tracks = gatheractionhookparams.ixam_tracks
    action_on_type = gatheractionhookparams.action_on_type

    # Remove duplicate actions.
    ixam_actions = list(set(ixam_actions))
    # sort animations alphabetically (case insensitive) so they have a defined order and match Ixam's Action list
    ixam_actions.sort(key = lambda a: a.name.lower())

    return [(ixam_action, ixam_tracks[ixam_action.name], action_on_type[ixam_action.name]) for ixam_action in ixam_actions]


def __is_armature_action(ixam_action) -> bool:
    for fcurve in ixam_action.fcurves:
        if is_bone_anim_channel(fcurve.data_path):
            return True
    return False

def __reset_bone_matrix(ixam_object, export_settings) -> None:
    if export_settings['gltf_export_reset_pose_bones'] is False:
        return

    # Only for armatures
    if ixam_object.type != "ARMATURE":
        return

    # Remove current action if any
    if ixam_object.animation_data and ixam_object.animation_data.action:
        ixam_object.animation_data.action = None

    # Resetting bones TRS to avoid to keep not keyed value on a future action set
    for bone in ixam_object.pose.bones:
        bone.matrix_basis = Matrix()
