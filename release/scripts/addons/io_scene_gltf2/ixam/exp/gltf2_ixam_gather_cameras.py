# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Ixam-IO authors.

from io_scene_gltf2.ixam.exp.gltf2_ixam_gather_cache import cached
from ..com.gltf2_ixam_extras import generate_extras
from io_scene_gltf2.io.com import gltf2_io
from io_scene_gltf2.io.exp.gltf2_io_user_extensions import export_user_extensions

import bpy
import math


@cached
def gather_camera(ixam_camera, export_settings):
    if not __filter_camera(ixam_camera, export_settings):
        return None

    camera = gltf2_io.Camera(
        extensions=__gather_extensions(ixam_camera, export_settings),
        extras=__gather_extras(ixam_camera, export_settings),
        name=__gather_name(ixam_camera, export_settings),
        orthographic=__gather_orthographic(ixam_camera, export_settings),
        perspective=__gather_perspective(ixam_camera, export_settings),
        type=__gather_type(ixam_camera, export_settings)
    )

    export_user_extensions('gather_camera_hook', export_settings, camera, ixam_camera)

    return camera


def __filter_camera(ixam_camera, export_settings):
    return bool(__gather_type(ixam_camera, export_settings))


def __gather_extensions(ixam_camera, export_settings):
    return None


def __gather_extras(ixam_camera, export_settings):
    if export_settings['gltf_extras']:
        return generate_extras(ixam_camera)
    return None


def __gather_name(ixam_camera, export_settings):
    return ixam_camera.name


def __gather_orthographic(ixam_camera, export_settings):
    if __gather_type(ixam_camera, export_settings) == "orthographic":
        orthographic = gltf2_io.CameraOrthographic(
            extensions=None,
            extras=None,
            xmag=None,
            ymag=None,
            zfar=None,
            znear=None
        )

        _render = bpy.context.scene.render
        scene_x = _render.resolution_x * _render.pixel_aspect_x
        scene_y = _render.resolution_y * _render.pixel_aspect_y
        scene_square = max(scene_x, scene_y)
        del _render

        # `Camera().ortho_scale` (and also FOV FTR) maps to the maximum of either image width or image height— This is the box that gets shown from camera view with the checkbox `.show_sensor = True`.

        orthographic.xmag = ixam_camera.ortho_scale * (scene_x / scene_square) / 2
        orthographic.ymag = ixam_camera.ortho_scale * (scene_y / scene_square) / 2

        orthographic.znear = ixam_camera.clip_start
        orthographic.zfar = ixam_camera.clip_end

        return orthographic
    return None


def __gather_perspective(ixam_camera, export_settings):
    if __gather_type(ixam_camera, export_settings) == "perspective":
        perspective = gltf2_io.CameraPerspective(
            aspect_ratio=None,
            extensions=None,
            extras=None,
            yfov=None,
            zfar=None,
            znear=None
        )

        _render = bpy.context.scene.render
        width = _render.pixel_aspect_x * _render.resolution_x
        height = _render.pixel_aspect_y * _render.resolution_y
        perspective.aspect_ratio = width / height
        del _render

        if width >= height:
            if ixam_camera.sensor_fit != 'VERTICAL':
                perspective.yfov = 2.0 * math.atan(math.tan(ixam_camera.angle * 0.5) / perspective.aspect_ratio)
            else:
                perspective.yfov = ixam_camera.angle
        else:
            if ixam_camera.sensor_fit != 'HORIZONTAL':
                perspective.yfov = ixam_camera.angle
            else:
                perspective.yfov = 2.0 * math.atan(math.tan(ixam_camera.angle * 0.5) / perspective.aspect_ratio)

        perspective.znear = ixam_camera.clip_start
        perspective.zfar = ixam_camera.clip_end

        return perspective
    return None


def __gather_type(ixam_camera, export_settings):
    if ixam_camera.type == 'PERSP':
        return "perspective"
    elif ixam_camera.type == 'ORTHO':
        return "orthographic"
    return None
