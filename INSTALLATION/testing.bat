echo off
where stevensegal

IF %ERRORLEVEL% NEQ 0 (
	echo "stevie "
)

where python
IF %ERRORLEVEL% NEQ 0 (
	echo "NOT SET UP PROPERlY"
) ELSE (
	echo "set up properly"
)


pause

IF EXISTS C:\Python27 (
	ECHO STEVIE
)

if EXISTS ..\flaskTest.py (
	echo wonder
)


PAUSE