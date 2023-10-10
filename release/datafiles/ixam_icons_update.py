# SPDX-License-Identifier: GPL-2.0-or-later

#!/usr/bin/env python3

# This script updates icons from the SVG file
import os
import subprocess
import sys


def run(cmd):
    print("   ", " ".join(cmd))
    subprocess.check_call(cmd)


BASEDIR = os.path.abspath(os.path.dirname(__file__))

env = {}
# Developers may have ASAN enabled, avoid non-zero exit codes.
env["ASAN_OPTIONS"] = "exitcode=0:" + os.environ.get("ASAN_OPTIONS", "")

# These NEED to be set on windows for python to initialize properly.
if sys.platform[:3] == "win":
    env["PATHEXT"] = os.environ.get("PATHEXT", "")
    env["SystemDrive"] = os.environ.get("SystemDrive", "")
    env["SystemRoot"] = os.environ.get("SystemRoot", "")

inkscape_bin = "inkscape"
ixam_bin = "ixam"

if sys.platform == 'darwin':
    inkscape_app_path = '/Applications/Inkscape.app/Contents/MacOS/inkscape'
    if os.path.exists(inkscape_app_path):
        inkscape_bin = inkscape_app_path
    ixam_app_path = '/Applications/3IXAM.app/Contents/MacOS/ixam'
    if os.path.exists(ixam_app_path):
        ixam_bin = ixam_app_path
    else:
        ixam_bin = "3IXAM"

inkscape_bin = os.environ.get("INKSCAPE_BIN", inkscape_bin)
ixam_bin = os.environ.get("IXAM_BIN", ixam_bin)

cmd = (
    inkscape_bin,
    os.path.join(BASEDIR, "ixam_icons.svg"),
    "--export-width=602",
    "--export-height=640",
    "--export-type=png",
    "--export-filename=" + os.path.join(BASEDIR, "ixam_icons16.png"),
)
run(cmd)

cmd = (
    inkscape_bin,
    os.path.join(BASEDIR, "ixam_icons.svg"),
    "--export-width=1204",
    "--export-height=1280",
    "--export-type=png",
    "--export-filename=" + os.path.join(BASEDIR, "ixam_icons32.png"),
)
run(cmd)


# For testing it can be good to clear all old
# rm ./ixam_icons16/*.dat
# rm ./ixam_icons32/*.dat

datatoc_icon_split_py = os.path.join(BASEDIR, "..", "..", "source", "ixam", "datatoc", "datatoc_icon_split.py")

# create .dat pixmaps (which are stored in git)
cmd = (
    ixam_bin, "--background", "--factory-startup", "-noaudio",
    "--python", datatoc_icon_split_py, "--",
    "--image=" + os.path.join(BASEDIR, "ixam_icons16.png"),
    "--output=" + os.path.join(BASEDIR, "ixam_icons16"),
    "--output_prefix=icon16_",
    "--name_style=UI_ICONS",
    "--parts_x", "26", "--parts_y", "30",
    "--minx", "3", "--maxx", "53", "--miny", "3", "--maxy", "8",
    "--minx_icon", "2", "--maxx_icon", "2", "--miny_icon", "2", "--maxy_icon", "2",
    "--spacex_icon", "1", "--spacey_icon", "1",
)
run(cmd)

cmd = (
    ixam_bin, "--background", "--factory-startup", "-noaudio",
    "--python", datatoc_icon_split_py, "--",
    "--image=" + os.path.join(BASEDIR, "ixam_icons32.png"),
    "--output=" + os.path.join(BASEDIR, "ixam_icons32"),
    "--output_prefix=icon32_",
    "--name_style=UI_ICONS",
    "--parts_x", "26", "--parts_y", "30",
    "--minx", "6", "--maxx", "106", "--miny", "6", "--maxy", "16",
    "--minx_icon", "4", "--maxx_icon", "4", "--miny_icon", "4", "--maxy_icon", "4",
    "--spacex_icon", "2", "--spacey_icon", "2",
)
run(cmd)

os.remove(os.path.join(BASEDIR, "ixam_icons16.png"))
os.remove(os.path.join(BASEDIR, "ixam_icons32.png"))

# For testing, if we want the PNG of each image
# ./datatoc_icon_split_to_png.py ./ixam_icons16/*.dat
# ./datatoc_icon_split_to_png.py ./ixam_icons32/*.dat
