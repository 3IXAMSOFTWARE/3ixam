set IXAM_DIR_NOSPACES=%IXAM_DIR: =%

if not "%IXAM_DIR%"=="%IXAM_DIR_NOSPACES%" (
	echo There are spaces detected in the build path "%IXAM_DIR%", this is currently not supported, exiting....
	exit /b 1
)