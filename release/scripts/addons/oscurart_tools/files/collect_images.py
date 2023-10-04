

# <pep8 compliant>

import bpy
from bpy.types import Operator
import os
import shutil


class collectImagesOsc(Operator):
    """Collect all images in the ixam file and put them in IMAGES folder"""
    bl_idname = "file.collect_all_images"
    bl_label = "Collect Images"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        imagespath = "%s/IMAGES"  % (os.path.dirname(bpy.data.filepath))

        if not os.path.exists(imagespath):
            os.mkdir(imagespath)

        bpy.ops.file.make_paths_absolute()

        for image in bpy.data.images:
            try:
                image.update()

                if image.has_data:
                    if not os.path.exists(os.path.join(imagespath,os.path.basename(image.filepath))):
                        shutil.copy(image.filepath, os.path.join(imagespath,os.path.basename(image.filepath)))
                        image.filepath = os.path.join(imagespath,os.path.basename(image.filepath))
                    else:
                        print("%s exists." % (image.name))
                else:
                    print("%s missing path." % (image.name))
            except:
                print("%s missing path." % (image.name))

        bpy.ops.file.make_paths_relative()

        return {'FINISHED'}
