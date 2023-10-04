# SPDX-License-Identifier: GPL-2.0-or-later

import time

import bpy
from bpy.props import *



class curvetoolsSelectedObjectHeader(bpy.types.Header):
    bl_label = "Selection"
    bl_space_type = "VIEW_3D"

    def __init__(self):
        self.update()


    def update(self):
        ixamSelectedObjects = bpy.context.selected_objects
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects

        selectedObjectsToRemove = []
        for selectedObject in selectedObjects:
            if not selectedObject.IsElementOf(ixamSelectedObjects): selectedObjectsToRemove.append(selectedObject)
        for selectedObject in selectedObjectsToRemove: selectedObjects.remove(selectedObject)

        ixamObjectsToAdd = []
        for ixamObject in ixamSelectedObjects:
            if not curvetoolsSelectedObject.ListContains(selectedObjects, ixamObject): ixamObjectsToAdd.append(ixamObject)
        for ixamObject in ixamObjectsToAdd:
            newSelectedObject = curvetoolsSelectedObject(ixamObject)
            selectedObjects.append(newSelectedObject)


    def draw(self, context):
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        nrSelectedObjects = len(selectedObjects)

        layout = self.layout
        row = layout.row()
        row.label(text="Sel: " + str(nrSelectedObjects))


class curvetoolsSelectedObject(bpy.types.PropertyGroup):
    name: StringProperty(name = "name", default = "??")


    @staticmethod
    def UpdateThreadTarget(lock, sleepTime, selectedObjectNames, selectedIxamObjectNames):
        time.sleep(sleepTime)

        newSelectedObjectNames = []

        for name in selectedObjectNames:
            if name in selectedIxamObjectNames: newSelectedObjectNames.append(name)

        for name in selectedIxamObjectNames:
            if not (name in selectedObjectNames): newSelectedObjectNames.append(name)

        # sometimes it still complains about the context
        try:
            nrNewSelectedObjects = len(newSelectedObjectNames)
            bpy.context.scene.curvetools.NrSelectedObjects = nrNewSelectedObjects

            selectedObjects = bpy.context.scene.curvetools.SelectedObjects
            selectedObjects.clear()
            for i in range(nrNewSelectedObjects): selectedObjects.add()
            for i, newSelectedObjectName in enumerate(newSelectedObjectNames):
                selectedObjects[i].name = newSelectedObjectName
        except: pass


    @staticmethod
    def GetSelectedObjectNames():
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects

        rvNames = []
        selectedObjectValues = selectedObjects.values()
        for selectedObject in selectedObjectValues: rvNames.append(selectedObject.name)

        return rvNames


    @staticmethod
    def GetSelectedIxamObjectNames():
        ixamSelectedObjects = bpy.context.selected_objects

        rvNames = []
        for blObject in ixamSelectedObjects: rvNames.append(blObject.name)

        return rvNames

def register():
    for cls in classes:
        bpy.utils.register_class(operators)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(operators)

if __name__ == "__main__":
    register()

operators = [
    curvetoolsSelectedObject,
    ]
