

# <pep8 compliant>

import bpy



# ------------------------------------ SELECTION -------------------------
bpy.selection_osc = []


def select_osc():
    if bpy.context.mode == "OBJECT":
        obj = bpy.context.object
        sel = len(bpy.context.selected_objects)

        if sel == 0:
            bpy.selection_osc = []
        else:
            if sel == 1:
                bpy.selection_osc = []
                bpy.selection_osc.append(obj)
            elif sel > len(bpy.selection_osc):
                for sobj in bpy.context.selected_objects:
                    if (sobj in bpy.selection_osc) is False:
                        bpy.selection_osc.append(sobj)

            elif sel < len(bpy.selection_osc):
                for it in bpy.selection_osc:
                    if (it in bpy.context.selected_objects) is False:
                        bpy.selection_osc.remove(it)


class OSSELECTION_HT_OscSelection(bpy.types.Header):
    bl_label = "Selection Osc"
    bl_space_type = "VIEW_3D"

    def __init__(self):
        select_osc()

    def draw(self, context):
        """
        layout = self.layout
        row = layout.row()
        row.label(text="Sels: "+str(len(bpy.selection_osc)))
        """
