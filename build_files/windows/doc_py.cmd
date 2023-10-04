set SOURCEDIR=%IXAM_DIR%/doc/python_api/sphinx-in
set BUILDDIR=%IXAM_DIR%/doc/python_api/sphinx-out
if "%BF_LANG%" == "" set BF_LANG=en
set SPHINXOPTS=-j auto -D language=%BF_LANG%

call "%~dp0\find_sphinx.cmd"

if EXIST "%SPHINX_BIN%" (
    goto detect_sphinx_done
)

echo unable to locate sphinx-build, run "set sphinx_BIN=full_path_to_sphinx-build.exe"
exit /b 1

:detect_sphinx_done

call "%~dp0\find_ixam.cmd"

if EXIST "%IXAM_BIN%" (
    goto detect_ixam_done
)

echo unable to locate ixam, run "set IXAM_BIN=full_path_to_ixam.exe"
exit /b 1

:detect_ixam_done

%IXAM_BIN% ^
	--background -noaudio --factory-startup ^
	--python %IXAM_DIR%/doc/python_api/sphinx_doc_gen.py

"%SPHINX_BIN%" -b html %SPHINXOPTS% %O% %SOURCEDIR% %BUILDDIR%

:EOF
