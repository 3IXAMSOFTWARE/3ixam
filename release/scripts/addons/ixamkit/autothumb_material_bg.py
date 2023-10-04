


if "bpy" in locals():
    from importlib import reload

    utils = reload(utils)
    append_link = reload(append_link)
    bg_ixam = reload(bg_ixam)
else:
    from ixamkit import utils, append_link, bg_ixam

import sys, json, math
import bpy
from pathlib import Path

IXAMKIT_EXPORT_TEMP_DIR = sys.argv[-1]
IXAMKIT_THUMBNAIL_PATH = sys.argv[-2]
IXAMKIT_EXPORT_FILE_INPUT = sys.argv[-3]
IXAMKIT_EXPORT_DATA = sys.argv[-4]


def render_thumbnails():
    bpy.ops.render.render(write_still=True, animation=False)


def unhide_collection(cname):
    collection = bpy.context.scene.collection.children[cname]
    collection.hide_viewport = False
    collection.hide_render = False
    collection.hide_select = False


if __name__ == "__main__":
    try:
        bg_ixam.progress('preparing thumbnail scene')
        with open(IXAMKIT_EXPORT_DATA, 'r') as s:
            data = json.load(s)
            # append_material(file_name, matname = None, link = False, fake_user = True)
        mat = append_link.append_material(file_name=IXAMKIT_EXPORT_FILE_INPUT, matname=data["material"], link=True,
                                          fake_user=False)

        user_preferences = bpy.context.preferences.addons['ixamkit'].preferences

        s = bpy.context.scene

        colmapdict = {
            'BALL': 'Ball',
            'CUBE': 'Cube',
            'FLUID': 'Fluid',
            'CLOTH': 'Cloth',
            'HAIR': 'Hair'
        }

        unhide_collection(colmapdict[data["thumbnail_type"]])
        if data['thumbnail_background']:
            unhide_collection('Background')
            bpy.data.materials["bg checker colorable"].node_tree.nodes['input_level'].outputs['Value'].default_value \
                = data['thumbnail_background_lightness']
        tscale = data["thumbnail_scale"]
        bpy.context.view_layer.objects['scaler'].scale = (tscale, tscale, tscale)
        bpy.context.view_layer.update()
        for ob in bpy.context.visible_objects:
            if ob.name[:15] == 'MaterialPreview':
                ob.material_slots[0].material = mat
                ob.data.texspace_size.x = 1 / tscale
                ob.data.texspace_size.y = 1 / tscale
                ob.data.texspace_size.z = 1 / tscale
                if data["adaptive_subdivision"] == True:
                    ob.cycles.use_adaptive_subdivision = True

                else:
                    ob.cycles.use_adaptive_subdivision = False
                ts = data['texture_size_meters']
                if data["thumbnail_type"] in ['BALL', 'CUBE', 'CLOTH']:
                   utils.automap(ob.name, tex_size = ts / tscale, just_scale = True, bg_exception=True)
        bpy.context.view_layer.update()

        s.cycles.volume_step_size = tscale * .1

        if user_preferences.thumbnail_use_gpu:
            bpy.context.scene.cycles.device = 'GPU'

        s.cycles.samples = data['thumbnail_samples']
        bpy.context.view_layer.cycles.use_denoising = data['thumbnail_denoising']

        # import ixam's HDR here
        hdr_path = Path('datafiles/studiolights/world/interior.exr')
        bpath = Path(bpy.utils.resource_path('LOCAL'))
        ipath = bpath / hdr_path
        ipath = str(ipath)

        # this  stuff is for mac and possibly linux. For ixam // means relative path.
        # for Mac, // means start of absolute path
        if ipath.startswith('//'):
            ipath = ipath[1:]

        img = bpy.data.images['interior.exr']
        img.filepath = ipath
        img.reload()

        bpy.context.scene.render.resolution_x = int(data['thumbnail_resolution'])
        bpy.context.scene.render.resolution_y = int(data['thumbnail_resolution'])

        bpy.context.scene.render.filepath = IXAMKIT_THUMBNAIL_PATH
        bg_ixam.progress('rendering thumbnail')
        render_thumbnails()
        bg_ixam.progress('background autothumbnailer finished successfully')


    except Exception as e:
        print(e)
        import traceback

        traceback.print_exc()

        sys.exit(1)