# This program is a free addon; you can redistribute it and/or edit
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# This addon was created with the Serpens - Visual Scripting Addon.
# This code is generated from nodes and is not intended for manual editing, but you might as well edit it, because you can always redownload it.
# You can find out more about Serpens at <https://3ixam.com/products/serpens>.


bl_info = {
    "name": "Camera Size Presets",
    "description": "video and photo presets for camera aspect ratio",
    "author": "Tobin",
    "version": (1, 14, 1),
    "ixam": (2, 80, 0),
    "location": "Properties > Output Properties > Format",
    "warning": "",
    "wiki_url": "https://wiki.3ixam.com/camera-size-presets-for-3ixam/",
    "category": "User Interface"
}

###############   IMPORTS
import bpy
from bpy.utils import previews
import os
import math
from bpy.app.handlers import persistent


###############   INITALIZE VARIABLES
###############   SERPENS FUNCTIONS
def exec_line(line):
    exec(line)

def sn_print(tree_name, *args):
    if tree_name in bpy.data.node_groups:
        item = bpy.data.node_groups[tree_name].sn_graphs[0].prints.add()
        for arg in args:
            item.value += str(arg) + ";;;"
        if bpy.context and bpy.context.screen:
            for area in bpy.context.screen.areas:
                area.tag_redraw()
    print(*args)

def sn_cast_string(value):
    return str(value)

def sn_cast_boolean(value):
    if type(value) == tuple:
        for data in value:
            if bool(data):
                return True
        return False
    return bool(value)

def sn_cast_float(value):
    if type(value) == str:
        try:
            value = float(value)
            return value
        except:
            return float(bool(value))
    elif type(value) == tuple:
        return float(value[0])
    elif type(value) == list:
        return float(len(value))
    elif not type(value) in [float, int, bool]:
        try:
            value = len(value)
            return float(value)
        except:
            return float(bool(value))
    return float(value)

def sn_cast_int(value):
    return int(sn_cast_float(value))

##############   VISIT 3ixam.NET IF YOU VALUE THIS ADDON

def sn_cast_boolean_vector(value, size):
    if type(value) in [str, bool, int, float]:
        return_value = []
        for i in range(size):
            return_value.append(bool(value))
        return tuple(return_value)
    elif type(value) == tuple:
        return_value = []
        for i in range(size):
            return_value.append(bool(value[i]) if len(value) > i else bool(value[0]))
        return tuple(return_value)
    elif type(value) == list:
        return sn_cast_boolean_vector(tuple(value), size)
    else:
        try:
            value = tuple(value)
            return sn_cast_boolean_vector(value, size)
        except:
            return sn_cast_boolean_vector(bool(value), size)

def sn_cast_float_vector(value, size):
    if type(value) in [str, bool, int, float]:
        return_value = []
        for i in range(size):
            return_value.append(sn_cast_float(value))
        return tuple(return_value)
    elif type(value) == tuple:
        return_value = []
        for i in range(size):
            return_value.append(sn_cast_float(value[i]) if len(value) > i else sn_cast_float(value[0]))
        return tuple(return_value)
    elif type(value) == list:
        return sn_cast_float_vector(tuple(value), size)
    else:
        try:
            value = tuple(value)
            return sn_cast_float_vector(value, size)
        except:
            return sn_cast_float_vector(sn_cast_float(value), size)

def sn_cast_int_vector(value, size):
    return tuple(map(int, sn_cast_float_vector(value, size)))

def sn_cast_color(value, use_alpha):
    length = 4 if use_alpha else 3
    value = sn_cast_float_vector(value, length)
    tuple_list = []
    for data in range(length):
        data = value[data] if len(value) > data else value[0]
        tuple_list.append(sn_cast_float(min(1, max(0, data))))
    return tuple(tuple_list)

def sn_cast_list(value):
    if type(value) in [str, tuple, list]:
        return list(value)
    elif type(value) in [int, float, bool]:
        return [value]
    else:
        try:
            value = list(value)
            return value
        except:
            return [value]

def sn_cast_blend_data(value):
    if hasattr(value, "bl_rna"):
        return value
    elif type(value) in [tuple, bool, int, float, list]:
        return None
    elif type(value) == str:
        try:
            value = eval(value)
            return value
        except:
            return None
    else:
        return None


def sn_cast_enum(string, enum_values):
    for item in enum_values:
        if item[1] == string:
            return item[0]
        elif item[0] == string.upper():
            return item[0]
    return string


###############   IMPERATIVE CODE
#######   Camera Size Presets
@persistent
def load_pre_handler_67D48(dummy):
    bpy.context.scene.name_of_menu = r"1920 x 1080 - Full HD "


###############   EVALUATED CODE
#######   Camera Size Presets
def sn_prepend_panel_79D36(self,context):
    try:
        layout = self.layout
        row = layout.row(align=False)
        row.enabled = True
        row.alert = False
        row.scale_x = 1.0
        row.scale_y = 1.0
        row.label(text=r"",icon_value=0)
        row.menu("SNA_MT_New_Menu_7317B",text=bpy.context.scene.name_of_menu,icon_value=0)
    except Exception as exc:
        print(str(exc) + " | Error in Render Format when adding to panel")
#Twitter

class SNA_OT_Twitter_Post(bpy.types.Operator):
    bl_idname = "sna.twitter_post"
    bl_label = "Twitter Post"
    bl_description = "Change aspect ratio to Twitter Post"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Twitter Post")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 900
            bpy.context.scene.render.resolution_y = 450
            bpy.context.scene.name_of_menu = r"900 x 450 - Twitter Post"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Twitter Post")
        return self.execute(context)

#Profile Picture

class SNA_OT_Profile(bpy.types.Operator):
    bl_idname = "sna.profile"
    bl_label = "Profile"
    bl_description = "Change aspect ratio to Profile Picture"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Profile")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 500
            bpy.context.scene.render.resolution_y = 500
            bpy.context.scene.name_of_menu = r"500 x 500 - Profile Picture"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Profile")
        return self.execute(context)

#Facebook

class SNA_OT_Facebook(bpy.types.Operator):
    bl_idname = "sna.facebook"
    bl_label = "Facebook"
    bl_description = "Change aspect ratio to Facebook"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Facebook")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1200
            bpy.context.scene.render.resolution_y = 630
            bpy.context.scene.name_of_menu = r"1200 x 630 - Facebook Post"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Facebook")
        return self.execute(context)

#Story(IG, TikTok etc.)

class SNA_OT_Story(bpy.types.Operator):
    bl_idname = "sna.story"
    bl_label = "Story"
    bl_description = "Change aspect ratio to Story"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Story")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1080
            bpy.context.scene.render.resolution_y = 1920
            bpy.context.scene.name_of_menu = r"1080 x 1920 - Story"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Story")
        return self.execute(context)

#12x18 inches
    
class SNA_OT_Sn_1218(bpy.types.Operator):
    bl_idname = "sna.sn_1218"
    bl_label = "1218"
    bl_description = "Change aspect ratio to 12 x 18 inches"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 1218")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 3600
            bpy.context.scene.render.resolution_y = 5400
            bpy.context.scene.name_of_menu = r"3600 x 5400 - 12 x 18 Inches"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 1218")
        return self.execute(context)

#Legal Letter Size (I think)

class SNA_OT_Sn_8511(bpy.types.Operator):
    bl_idname = "sna.sn_8511"
    bl_label = "8.511"
    bl_description = "Change aspect ratio to 8.5 x 11 inches"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 8.511")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 3400
            bpy.context.scene.render.resolution_y = 4400
            bpy.context.scene.name_of_menu = r"3400 x 4400 - 8.5 x 11 Inches"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 8.511")
        return self.execute(context)

#10x8 Inches

class SNA_OT_Sn_108(bpy.types.Operator):
    bl_idname = "sna.sn_108"
    bl_label = "108"
    bl_description = "Change aspect ratio to 10 x 8 inches"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 108")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 2400
            bpy.context.scene.render.resolution_y = 3000
            bpy.context.scene.name_of_menu = r"2400 x 3000 - 10 x 8 Inches"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 108")
        return self.execute(context)

#5x7 Inches

class SNA_OT_Sn_57(bpy.types.Operator):
    bl_idname = "sna.sn_57"
    bl_label = "57"
    bl_description = "Change aspect ratio to 5 x 7 inches"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 57")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1500
            bpy.context.scene.render.resolution_y = 2100
            bpy.context.scene.name_of_menu = r"1500 x 2100 - 5 x 7 Inches"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 57")
        return self.execute(context)

#High Definition

class SNA_OT_Hd(bpy.types.Operator):
    bl_idname = "sna.hd"
    bl_label = "HD"
    bl_description = "Change aspect ratio to HD"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of HD")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1280
            bpy.context.scene.render.resolution_y = 720
            bpy.context.scene.name_of_menu = r"1280 x 720 - HD"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of HD")
        return self.execute(context)

#Stinky Definition

class SNA_OT_Sd(bpy.types.Operator):
    bl_idname = "sna.sd"
    bl_label = "SD"
    bl_description = "Change aspect ratio to SD"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of SD")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 640
            bpy.context.scene.render.resolution_y = 480
            bpy.context.scene.name_of_menu = r"640 x 480 - SD"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of SD")
        return self.execute(context)

#Full High Definition

class SNA_OT_Full_Hd(bpy.types.Operator):
    bl_idname = "sna.full_hd"
    bl_label = "Full HD"
    bl_description = "Change aspect ratio to Full HD"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Full HD")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1920
            bpy.context.scene.render.resolution_y = 1080
            bpy.context.scene.name_of_menu = r"1920 x 1080 - Full HD"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Full HD")
        return self.execute(context)

#2k, but it might actually be Quad HD, sorry. I'm not sure.

class SNA_OT_Sn_2K(bpy.types.Operator):
    bl_idname = "sna.sn_2k"
    bl_label = "2K"
    bl_description = "Change aspect ratio to 2K"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 2K")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 2560
            bpy.context.scene.render.resolution_y = 1440
            bpy.context.scene.name_of_menu = r"2560 x 1440 - 2K"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 2K")
        return self.execute(context)

#4k, I've double checked and it definately is.

class SNA_OT_Sn_4K(bpy.types.Operator):
    bl_idname = "sna.sn_4k"
    bl_label = "4K"
    bl_description = "Change aspect ratio to 4K"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 4K")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 3840
            bpy.context.scene.render.resolution_y = 2160
            bpy.context.scene.name_of_menu = r"3840 x 2160 - 4K"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 4K")
        return self.execute(context)

#6x4 Inches, I'm not sure when this ones useful, but I added it anyway.

class SNA_OT_Sn_64(bpy.types.Operator):
    bl_idname = "sna.sn_64"
    bl_label = "64"
    bl_description = "Change aspect ratio to 6 x 4 inches"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of 64")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1200
            bpy.context.scene.render.resolution_y = 1800
            bpy.context.scene.name_of_menu = r"1200 x 1800 - 6 x 4 Inches"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of 64")
        return self.execute(context)

#Instagram, sorry for the unorganized layout.

class SNA_OT_Instagram(bpy.types.Operator):
    bl_idname = "sna.instagram"
    bl_label = "Instagram"
    bl_description = "Change aspect ratio to Instagram post"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Instagram")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = 1080
            bpy.context.scene.render.resolution_y = 1080
            bpy.context.scene.name_of_menu = r"1080 x 1080 - Instagram Post"
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Instagram")
        return self.execute(context)

#This is a custom one.

class SNA_OT_Custom_2(bpy.types.Operator):
    bl_idname = "sna.custom_2"
    bl_label = "Custom 2"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Custom 2")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = context.preferences.addons['camera_size_presets'].preferences.resolution_x_2
            bpy.context.scene.render.resolution_y = context.preferences.addons['camera_size_presets'].preferences.resolution_y_2
            bpy.context.scene.name_of_menu = context.preferences.addons['camera_size_presets'].preferences.option_name_2
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Custom 2")
        return self.execute(context)

#This one is custom too.

class SNA_OT_Custom_3(bpy.types.Operator):
    bl_idname = "sna.custom_3"
    bl_label = "Custom 3"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Custom 3")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = context.preferences.addons['camera_size_presets'].preferences.resolution_x_3
            bpy.context.scene.render.resolution_y = context.preferences.addons['camera_size_presets'].preferences.resolution_y_3
            bpy.context.scene.name_of_menu = context.preferences.addons['camera_size_presets'].preferences.option_name_3
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Custom 3")
        return self.execute(context)

#This one is custom three! Just kidding, it's number four.

class SNA_OT_Custom_4(bpy.types.Operator):
    bl_idname = "sna.custom_4"
    bl_label = "Custom 4"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Custom 4")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = context.preferences.addons['camera_size_presets'].preferences.resolution_x_4
            bpy.context.scene.render.resolution_y = context.preferences.addons['camera_size_presets'].preferences.resolution_y_4
            bpy.context.scene.name_of_menu = context.preferences.addons['camera_size_presets'].preferences.option_name_4
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Custom 4")
        return self.execute(context)

#Custom five, here.

class SNA_OT_Custom_5(bpy.types.Operator):
    bl_idname = "sna.custom_5"
    bl_label = "Custom 5"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Custom 5")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = context.preferences.addons['camera_size_presets'].preferences.resolution_x_5
            bpy.context.scene.render.resolution_y = context.preferences.addons['camera_size_presets'].preferences.resolution_y_5
            bpy.context.scene.name_of_menu = context.preferences.addons['camera_size_presets'].preferences.option_name_5
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Custom 5")
        return self.execute(context)


class SNA_MT_New_Menu_7317B(bpy.types.Menu):
    bl_idname = "SNA_MT_New_Menu_7317B"
    bl_label = "New Menu"


    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        try:
            layout = self.layout
            layout.label(text=r"Video",icon_value=111)
            op = layout.operator("sna.sd",text=r"640 x 480 - SD",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.hd",text=r"1280 x 720 - HD",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.full_hd",text=r"1920 x 1080 - Full HD",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.sn_2k",text=r"2560 x 1440 - 2K",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.sn_4k",text=r"3840 x 2160 - 4K",emboss=True,depress=False,icon_value=0)
            layout.label(text=r"Photo",icon_value=183)
            op = layout.operator("sna.sn_64",text=r"1200 x 1800 - 6 x 4 Inches",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.sn_57",text=r"1500 x 2100 - 5 x 7 Inches",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.sn_108",text=r"2400 x 3000 - 10 x 8 Inches",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.sn_8511",text=r"3400 x 4400 - 8.5 x 11 Inches",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.sn_1218",text=r"3600 x 5400 - 12 x 18 Inches",emboss=True,depress=False,icon_value=0)
            layout.label(text=r"Social",icon_value=231)
            op = layout.operator("sna.instagram",text=r"1080 x 1080 - Instagram Post",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.story",text=r"1080 x 1920 - Story",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.facebook",text=r"1200 x 630 - Facebook Post",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.profile",text=r"500 x 500 - Profile Picture",emboss=True,depress=False,icon_value=0)
            op = layout.operator("sna.twitter_post",text=r"900 x 450 - Twitter Post",emboss=True,depress=False,icon_value=0)
            # layout.label(text=r"Custom",icon_value=197)
            # op = layout.operator("sna.custom_1",text=context.preferences.addons['camera_size_presets'].preferences.option_name_1,emboss=True,depress=False,icon_value=0)
            # op = layout.operator("sna.custom_2",text=context.preferences.addons['camera_size_presets'].preferences.option_name_2,emboss=True,depress=False,icon_value=0)
            # op = layout.operator("sna.custom_3",text=context.preferences.addons['camera_size_presets'].preferences.option_name_3,emboss=True,depress=False,icon_value=0)
            # op = layout.operator("sna.custom_4",text=context.preferences.addons['camera_size_presets'].preferences.option_name_4,emboss=True,depress=False,icon_value=0)
            # op = layout.operator("sna.custom_5",text=context.preferences.addons['camera_size_presets'].preferences.option_name_5,emboss=True,depress=False,icon_value=0)
        except Exception as exc:
            print(str(exc) + " | Error in New Menu menu")

#This is the first custom one, I don't know why it's at the bottom, maybe Serpens knows.

class SNA_OT_Custom_1(bpy.types.Operator):
    bl_idname = "sna.custom_1"
    bl_label = "Custom 1"
    bl_description = "Change aspect ratio"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        try:
            pass
        except Exception as exc:
            print(str(exc) + " | Error in execute function of Custom 1")
        return {"FINISHED"}

    def invoke(self, context, event):
        try:
            bpy.context.scene.render.resolution_x = context.preferences.addons['camera_size_presets'].preferences.resolution_x_1
            bpy.context.scene.render.resolution_y = context.preferences.addons['camera_size_presets'].preferences.resolution_y_1
            bpy.context.scene.name_of_menu = context.preferences.addons['camera_size_presets'].preferences.option_name_1
        except Exception as exc:
            print(str(exc) + " | Error in invoke function of Custom 1")
        return self.execute(context)

#Hey look, if you do't like the code, you can just LEAVE IT ALONE!!

class SNA_AddonPreferences_F573A(bpy.types.AddonPreferences):
    bl_idname = 'camera_size_presets'
    resolution_x_1: bpy.props.IntProperty(name='Resolution X 1',description='',subtype='NONE',options=set(),default=100)
    resolution_y_1: bpy.props.IntProperty(name='Resolution Y 1',description='',subtype='NONE',options=set(),default=100)
    option_name_1: bpy.props.StringProperty(name='Option Name 1',description='',subtype='NONE',options=set(),default='Cutom 1')
    option_name_2: bpy.props.StringProperty(name='Option Name 2',description='',subtype='NONE',options=set(),default='Cutom 2')
    resolution_x_2: bpy.props.IntProperty(name='Resolution X 2',description='',subtype='NONE',options=set(),default=100)
    resolution_y_2: bpy.props.IntProperty(name='Resolution Y 2',description='',subtype='NONE',options=set(),default=100)
    option_name_3: bpy.props.StringProperty(name='Option Name 3',description='',subtype='NONE',options=set(),default='Cutom 3')
    resolution_x_3: bpy.props.IntProperty(name='Resolution X 3',description='',subtype='NONE',options=set(),default=100)
    resolution_y_3: bpy.props.IntProperty(name='Resolution Y 3',description='',subtype='NONE',options=set(),default=100)
    option_name_4: bpy.props.StringProperty(name='Option Name 4',description='',subtype='NONE',options=set(),default='Cutom 4')
    resolution_x_4: bpy.props.IntProperty(name='Resolution X 4',description='',subtype='NONE',options=set(),default=100)
    resolution_y_4: bpy.props.IntProperty(name='Resolution Y 4',description='',subtype='NONE',options=set(),default=100)
    option_name_5: bpy.props.StringProperty(name='Option Name 5',description='',subtype='NONE',options=set(),default='Cutom 5')
    resolution_x_5: bpy.props.IntProperty(name='Resolution X 5',description='',subtype='NONE',options=set(),default=100)
    resolution_y_5: bpy.props.IntProperty(name='Resolution Y 5',description='',subtype='NONE',options=set(),default=100)

    def draw(self, context):
        try:
            layout = self.layout
            row = layout.row(align=False)
            row.enabled = True
            row.alert = False
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.label(text=r"Preset Name",icon_value=0)
            row.label(text=r"Resolution X",icon_value=0)
            row.label(text=r"Resolution Y",icon_value=0)
            row = layout.row(align=False)
            row.enabled = True
            row.alert = False
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'option_name_1',icon_value=0,text=r"",emboss=True,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_x_1',text=r"",emboss=True,slider=False,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_y_1',text=r"",emboss=True,slider=False,)
            row = layout.row(align=False)
            row.enabled = True
            row.alert = False
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'option_name_2',icon_value=0,text=r"",emboss=True,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_x_2',text=r"",emboss=True,slider=False,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_y_2',text=r"",emboss=True,slider=False,)
            row = layout.row(align=False)
            row.enabled = True
            row.alert = False
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'option_name_3',icon_value=0,text=r"",emboss=True,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_x_3',text=r"",emboss=True,slider=False,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_y_3',text=r"",emboss=True,slider=False,)
            row = layout.row(align=False)
            row.enabled = True
            row.alert = False
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'option_name_4',icon_value=0,text=r"",emboss=True,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_x_4',text=r"",emboss=True,slider=False,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_y_4',text=r"",emboss=True,slider=False,)
            row = layout.row(align=False)
            row.enabled = True
            row.alert = False
            row.scale_x = 1.0
            row.scale_y = 1.0
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'option_name_5',icon_value=0,text=r"",emboss=True,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_x_5',text=r"",emboss=True,slider=False,)
            row.prop(context.preferences.addons['camera_size_presets'].preferences,'resolution_y_5',text=r"",emboss=True,slider=False,)
        except Exception as exc:
            print(str(exc) + " | Error in addon preferences")


###############   REGISTER ICONS
def sn_register_icons():
    icons = []
    bpy.types.Scene.camera_size_presets_icons = bpy.utils.previews.new()
    icons_dir = os.path.join( os.path.dirname( __file__ ), "icons" )
    for icon in icons:
        bpy.types.Scene.camera_size_presets_icons.load( icon, os.path.join( icons_dir, icon + ".png" ), 'IMAGE' )

def sn_unregister_icons():
    bpy.utils.previews.remove( bpy.types.Scene.camera_size_presets_icons )


###############   REGISTER PROPERTIES
def sn_register_properties():
    bpy.types.Scene.new_property = bpy.props.BoolProperty(name='New Property',description='Denoise',options=set(),default=True)
    bpy.types.Scene.name_of_menu = bpy.props.StringProperty(name='Name of Menu',description='',subtype='NONE',options=set(),default='1920 x 1080 - Full HD')

def sn_unregister_properties():
    del bpy.types.Scene.new_property
    del bpy.types.Scene.name_of_menu


###############   REGISTER ADDON
def register():
    sn_register_icons()
    sn_register_properties()
    bpy.utils.register_class(SNA_OT_Twitter_Post)
    bpy.utils.register_class(SNA_OT_Profile)
    bpy.utils.register_class(SNA_OT_Facebook)
    bpy.utils.register_class(SNA_OT_Story)
    bpy.utils.register_class(SNA_OT_Sn_1218)
    bpy.utils.register_class(SNA_OT_Sn_8511)
    bpy.utils.register_class(SNA_OT_Sn_108)
    bpy.utils.register_class(SNA_OT_Sn_57)
    bpy.utils.register_class(SNA_OT_Hd)
    bpy.utils.register_class(SNA_OT_Sd)
    bpy.utils.register_class(SNA_OT_Full_Hd)
    bpy.utils.register_class(SNA_OT_Sn_2K)
    bpy.utils.register_class(SNA_OT_Sn_4K)
    bpy.utils.register_class(SNA_OT_Sn_64)
    bpy.utils.register_class(SNA_OT_Instagram)
    bpy.app.handlers.load_pre.append(load_pre_handler_67D48)
    bpy.utils.register_class(SNA_OT_Custom_2)
    bpy.utils.register_class(SNA_OT_Custom_3)
    bpy.utils.register_class(SNA_OT_Custom_4)
    bpy.utils.register_class(SNA_OT_Custom_5)
    bpy.utils.register_class(SNA_MT_New_Menu_7317B)
    bpy.utils.register_class(SNA_OT_Custom_1)
    bpy.utils.register_class(SNA_AddonPreferences_F573A)
    bpy.types.RENDER_PT_format.prepend(sn_prepend_panel_79D36)


###############   UNREGISTER ADDON
def unregister():
    sn_unregister_icons()
    sn_unregister_properties()
    bpy.types.RENDER_PT_format.remove(sn_prepend_panel_79D36)
    bpy.utils.unregister_class(SNA_AddonPreferences_F573A)
    bpy.utils.unregister_class(SNA_OT_Custom_1)
    bpy.utils.unregister_class(SNA_MT_New_Menu_7317B)
    bpy.utils.unregister_class(SNA_OT_Custom_5)
    bpy.utils.unregister_class(SNA_OT_Custom_4)
    bpy.utils.unregister_class(SNA_OT_Custom_3)
    bpy.utils.unregister_class(SNA_OT_Custom_2)
    bpy.app.handlers.load_pre.remove(load_pre_handler_67D48)
    bpy.utils.unregister_class(SNA_OT_Instagram)
    bpy.utils.unregister_class(SNA_OT_Sn_64)
    bpy.utils.unregister_class(SNA_OT_Sn_4K)
    bpy.utils.unregister_class(SNA_OT_Sn_2K)
    bpy.utils.unregister_class(SNA_OT_Full_Hd)
    bpy.utils.unregister_class(SNA_OT_Sd)
    bpy.utils.unregister_class(SNA_OT_Hd)
    bpy.utils.unregister_class(SNA_OT_Sn_57)
    bpy.utils.unregister_class(SNA_OT_Sn_108)
    bpy.utils.unregister_class(SNA_OT_Sn_8511)
    bpy.utils.unregister_class(SNA_OT_Sn_1218)
    bpy.utils.unregister_class(SNA_OT_Story)
    bpy.utils.unregister_class(SNA_OT_Facebook)
    bpy.utils.unregister_class(SNA_OT_Profile)
    bpy.utils.unregister_class(SNA_OT_Twitter_Post)




#Why did you scroll down to the bottom?
if __name__ == "__main__":
    register()