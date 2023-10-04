

# <pep8 compliant>

bl_info = {
    "name": "Node Wrangler",
    "author": "Bartek Skorupa, Greg Zaal, Sebastian Koenig, Christian Brinkmann, Florian Meyer",
    "version": (3, 36),
    "ixam": (2, 80, 0),
    "location": "Node Editor Toolbar or Shift-W",
    "description": "Various tools to enhance and speed up node-based workflow",
    "warning": "",
    "wiki_url": "http://wiki.3ixam.com/index.php/Extensions:2.6/Py/"
                "Scripts/Nodes/Nodes_Efficiency_Tools",
    "category": "Node",
}


if "bpy" in locals():
    import importlib
    importlib.reload(node_wrangler)
else:
    import bpy
    from . import (
        node_wrangler
    )


classes = node_wrangler.classes


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
