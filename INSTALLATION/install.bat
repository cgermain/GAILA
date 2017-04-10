ECHO OFF

rem pseudocode:
rem if theres no pip, install pip
rem if theres no venv, install venv
rem create venv
rem enter venv
rem install modules that are needed
rem deactivate from venv
rem exit successfully


echo beginning setup ...

WHERE /r "c:\Python27" "python"
IF %ERRORLEVEL% NEQ 0 (
	echo "python is not installed, install python 2.7 for windows and then try again"
	echo "this installation expects a computer with vanilla python, if your computer has Anaconda or another python package, open install.bat in notepad and change all instances of c:\Python27 to the folder with your python executable"
	echo exiting . . .
	pause
	exit 1
)

WHERE perl
IF %ERRORLEVEL% NEQ 0 (
	echo "perl is not installed, install perl for windows and then try again"
	echo exiting . . .
	pause
	exit 1
)


WHERE /r "c:\Python27\Scripts" "pip"
IF %ERRORLEVEL% NEQ 0 (
	ECHO "NO PIP INSTALLED"
	echo installing pip now...
	VERIFY
	c:\Python27\Scripts get-pip.py
	ECHO "pip should be installed"
	WHERE /r "c:\Python27\Scripts" "pip"
	IF %ERRORLEVEL% NEQ 0 (
		ECHO "PIP INSTALLATION FAILED!"
		echo exiting . . .
		pause
		exit 1
	) ELSE (
		echo Installation worked!
	)
) ELSE (
	echo pip found
)


WHERE /r "c:\Python27\Scripts" "virtualenv"
IF %ERRORLEVEL% NEQ 0 (
	ECHO no virtualenv installed
	rem GOTO INSTALLVENV
	echo installing virtualenv now . . .
	verify
	c:\Python27\Scripts\pip install virtualenv
	echo virtualenv should be installed
	WHERE /r "c:\Python27\Scripts" "virtualenv"
	IF %ERRORLEVEL% NEQ 0 (
		echo "VIRTUALENV INSTALLATION FAILED!"
		echo exiting . . .
		pause
		exit 1
	) ELSE (
		echo Installation worked!
	)
) else (
	virtualenv found
)


echo "creating a virtualenv for this project, creatively naming it venv."
C:\Python27\Scripts\virtualenv ..\VENV
IF %ERRORLEVEL% NEQ 0 (
	echo error creating venv. installation failed.
	echo exiting . . .
	pause
	exit 1
)

echo "created virtualenv sucessfully"

echo "activating venv"
echo activating venv
CALL ..\VENV\Scripts\activate
echo "activated venv"

where deactivate
IF %ERRORLEVEL% NEQ 0 (
	echo error activating virtualenv, exiting so that nothing gets installed where it shouldn't.
	echo exiting . . .
	pause
	exit 1
)

echo upgrading pip
pip install --upgrade pip
echo pip upgraded, upgrading setuptools
pip install --upgrade setuptools
echo setuptools upgraded

echo "installing all modules (flask, pandas, numpy)"
echo installing flask
pip install flask
IF %ERRORLEVEL% NEQ 0 (
	echo error installing flask. installation failed.
	echo exiting . . . 
	pause
	exit 1
)

echo FLASK INSTALLED SUCESSFULLY


echo .
echo .
echo .
echo .

echo installing numpy. IT TAKES A VERY LONG TIME TO INSTALL, BE PREPARED!
TIMEOUT 5
pip install numpy -v
IF %ERRORLEVEL% NEQ 0 (
	echo error installing numpy. Installation failed
	echo exiting . . .
	pause
	exit 1
)

echo numpy installed


echo .
echo .
echo .
echo .


echo installing pandas
pip install pandas
IF %ERRORLEVEL% NEQ 0 (
	echo error installing pandas. Installation failed.
	echo exiting . . .
	pause
	exit 1
)


echo .
echo .
echo .
echo .


echo installing pyteomics
pip install pyteomics
IF %ERRORLEVEL% NEQ 0 (
	echo error installing pyteomics. Installation failed.
	echo exiting . . .
	pause
	exit 1
)

echo .
echo .
echo .
echo .


echo installing MatrixReal
call ppm install Math::MatrixReal
IF %ERRORLEVEL% NEQ 0 (
	echo error installing MatrixReal. Installation failed.
	echo exiting . . .
	pause
	exit 1
)

echo .
echo .
echo .
echo .

echo everything should be installed


echo deactivating venv
call deactivate


ECHO call VENV\Scripts\activate > ..\startup.bat
ECHO python flasktest.py >> ..\startup.bat
echo finished sucessfully!




:END
echo exiting script
pause