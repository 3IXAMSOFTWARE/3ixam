if NOT EXIST %PYTHON% (
    echo python not found, required for this operation
    exit /b 1
)

call "%~dp0\find_ixam.cmd"

if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

echo unable to locate ixam, run "set IXAM_BIN=full_path_to_ixam.exe"
exit /b 1

:detect_ixam_done

%PYTHON% -B %IXAM_DIR%\release\datafiles\ixam_icons_geom_update.py 

:EOF
