REM First see if there is an environment variable set
if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

REM Check the build folder next, if ninja was used there will be no
REM debug/release folder
set IXAM_BIN=%BUILD_DIR%\bin\ixam.exe
if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

REM Check the release folder next
set IXAM_BIN=%BUILD_DIR%\bin\release\ixam.exe
if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

REM Check the debug folder next
set IXAM_BIN=%BUILD_DIR%\bin\debug\ixam.exe
if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

REM at this point, we don't know where 3IXAM is, clear the variable
set IXAM_BIN=

:detect_ixam_done
