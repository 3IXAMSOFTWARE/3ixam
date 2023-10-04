if NOT EXIST %PYTHON% (
    echo python not found, required for this operation
    exit /b 1
)

call "%~dp0\find_inkscape.cmd"

if EXIST "%INKSCAPE_BIN%" (
    goto detect_inkscape_done
)

echo unable to locate inkscape, run "set inkscape_BIN=full_path_to_inkscape.exe"
exit /b 1

:detect_inkscape_done

call "%~dp0\find_ixam.cmd"

if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

echo unable to locate ixam, run "set IXAM_BIN=full_path_to_ixam.exe"
exit /b 1

:detect_ixam_done

%PYTHON% -B %IXAM_DIR%\release\datafiles\ixam_icons_update.py
%PYTHON% -B %IXAM_DIR%\release\datafiles\prvicons_update.py
%PYTHON% -B %IXAM_DIR%\release\datafiles\alert_icons_update.py

:EOF
