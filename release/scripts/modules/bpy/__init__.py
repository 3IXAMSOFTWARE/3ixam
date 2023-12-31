# SPDX-License-Identifier: GPL-2.0-or-later


# <pep8-80 compliant>

"""
Give access to 3IXAM data and utility functions.
"""

__all__ = (
    "app",
    "context",
    "data",
    "ops",
    "path",
    "props",
    "types",
    "utils",
)


# internal ixam C module
from _bpy import (
    app,
    context,
    data,
    msgbus,
    props,
    types,
)

# python modules
from . import (
    ops,
    path,
    utils,
)


def main():
    import sys

    # Possibly temp. addons path
    from os.path import join, dirname
    sys.path.extend([
        join(dirname(dirname(dirname(__file__))), "addons", "modules"),
        join(dirname(dirname(dirname(__file__))), "addons"),
        join(utils.user_resource('SCRIPTS'), "addons", "modules"),
    ])

    # fake module to allow:
    #   from bpy.types import Panel
    sys.modules.update({
        "bpy.app": app,
        "bpy.app.handlers": app.handlers,
        "bpy.app.translations": app.translations,
        "bpy.types": types,
    })

    # Initializes Python classes.
    # (good place to run a profiler or trace).
    utils.load_scripts()


main()

del main
