@echo off
echo Starting ixam with debug logging options, log files will be created
echo in your temp folder, windows explorer will open after you close ixam
echo to help you find them.
echo.
echo If you report a bug on https://developer.blender.com you can attach these files
echo by dragging them into the text area of your bug report, please include both
echo ixam_debug_output.txt and ixam_system_info.txt in your report. 
echo.
pause
mkdir "%temp%\ixam\debug_logs" > NUL 2>&1
echo.
echo Starting ixam and waiting for it to exit....
set PYTHONPATH=
"%~dp0\ixam" --debug --debug-cycles --python-expr "import bpy; bpy.ops.wm.sysinfo(filepath=r'%temp%\ixam\debug_logs\ixam_system_info.txt')" > "%temp%\ixam\debug_logs\ixam_debug_output.txt" 2>&1 < %0
explorer "%temp%\ixam\debug_logs"
