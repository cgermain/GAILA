ECHO OFF

rem pseudocode:
rem if theres no pip, install pip
rem if theres no venv, install venv
rem create venv
rem enter venv
rem install modules that are needed
rem deactivate from venv
rem exit successfully
rem
rem
rem
rem
rem
rem
rem


echo beginning setup ...

WHERE /r "c:\Python27" "python"
IF %ERRORLEVEL% NEQ 0 (
	echo "python is not installed, install python 2.7 for windows and then try again"
	GOTO END

)

GOTO CHECKFORPIP


:CHECKFORPIP

WHERE /r "c:\Python27\Scripts" "pip"
IF %ERRORLEVEL% NEQ 0 (
	ECHO "NO PIP INSTALLED"
	GOTO INSTALLPIP
)
echo pip found
GOTO CHECKFORVENV


:INSTALLPIP
echo installing pip now...
python get-pip.py
WHERE /r "c:\Python27\Scripts" "pip"
IF %ERRORLEVEL% NEQ 0 (
	ECHO "INSTALLATION FAILED"
	GOTO FINISHED
)
echo "pip installed successfully into C:\Python27\Scripts\pip.exe"
GOTO CHECKFORVENV


:CHECKFORVENV
WHERE /r "c:\Python27\Scripts" "virtualenv"
IF %ERRORLEVEL% NEQ 0 (
	ECHO no virtualenv installed
	GOTO INSTALLVENV
)
echo looks like we have virtualenv
GOTO CREATEVENV


:INSTALLVENV
ECHO isntalling venv
c:\Python27\Scripts\pip install virtualenv
ECHO virtualenv has been installed (hopefully)
WHERE /r "c:\Python27\Scripts" "virtualenv"
IF %ERRORLEVEL% NEQ 0 (
	echo error installing virtualenv
	GOTO FINISHED
)
echo "virtualenv installed correctly"
GOTO CREATEVENV

:CREATEVENV
echo "creating a virtualenv for this project, creatively naming it venv."
C:\Python27\Scripts\virtualenv ..\VENV
IF %ERRORLEVEL% NEQ 0 (
	echo error creating venv
	GOTO FINISHED
)

echo "created virtualenv sucessfully"
GOTO ACTIVATEVENV


:ACTIVATEVENV
echo "activating venv"
echo activating venv
CALL ..\VENV\Scripts\activate
echo "activated venv"
GOTO INSTALLMODULES


:INSTALLMODULES
echo "installing all modules (flask, pandas, numpy)"
echo installing flask
pip install flask
IF %ERRORLEVEL% NEQ 0 (
	echo error installing flask
	deactivate
	GOTO FINISHED
)

echo .
echo .
echo .
echo .

echo installing pandas
pip install pandas
IF %ERRORLEVEL% NEQ 0 (
	echo error installing flask
	deactivate
	GOTO FINISHED
)

echo .
echo .
echo .
echo .

echo installing numpy
pip install numpy
IF %ERRORLEVEL% NEQ 0 (
	echo error installing flask
	deactivate
	GOTO FINISHED
)
echo everything should be installed


:DEACTIVATEVENV
echo deactivating venv
call deactivate
GOTO CREATESTARTUPSCRIPT

:CREATESTARTUPSCRIPT

ECHO echo off > ..\startup.bat 
ECHO call VENV\Scripts\activate >> ..\startup.bat
ECHO python flasktest.py >> ..\startup.bat
GOTO FINISHEDSUCCESSFULLY



:FINISHED
echo "finished with script, but there were errors. Read above, and try again."
goto END


:FINISHEDSUCCESSFULLY
echo "finished sucessfully"
goto END


:END
echo exiting script
pause





