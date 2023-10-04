if "%GIT%" == "" (
	echo Git not found, cannot show hashes.
	goto EOF
)
cd "%IXAM_DIR%"
for /f "delims=" %%i in ('"%GIT%" rev-parse HEAD') do echo Branch_hash=%%i
cd "%IXAM_DIR%/release/datafiles/locale"
for /f "delims=" %%i in ('"%GIT%" rev-parse HEAD') do echo Locale_hash=%%i
cd "%IXAM_DIR%/release/scripts/addons"
for /f "delims=" %%i in ('"%GIT%" rev-parse HEAD') do echo Addons_Hash=%%i
cd "%IXAM_DIR%"
:EOF