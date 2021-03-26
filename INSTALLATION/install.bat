ECHO OFF

rem if theres no pip, install pip
rem if theres no venv, install venv
rem create venv
rem enter venv
rem install modules that are needed
rem deactivate from venv
rem exit successfully


echo Starting GAILA installation ...
 
py -3 --version > NUL
IF %ERRORLEVEL% NEQ 0 (
	echo Python is not installed, install Python 3 for Windows and then try again.
	echo Please make sure that Python is in your PATH.
	echo exiting . . .
	pause
	exit 1
)

WHERE perl > NUL
IF %ERRORLEVEL% NEQ 0 (
	echo Perl is not installed.  Install Perl for windows and then try again.
	echo Please make sure that Perl is in your PATH.
	echo exiting . . .
	pause
	exit 1
)

pip --version > NUL
IF %ERRORLEVEL% NEQ 0 (
	echo The Python package manager Pip is not installed.  Please download and try the GAILA installation again.
)

echo Creating a GAILA virtual environment.
python -m venv ..\GAILA_VENV
IF %ERRORLEVEL% NEQ 0 (
	echo error creating venv. installation failed.
	echo exiting . . .
	pause
	exit 1
)

echo \GAILA_VENV created sucessfully

echo activating 
CALL ..\GAILA_VENV\Scripts\activate
echo Activated GAILAVENV.

where deactivate
IF %ERRORLEVEL% NEQ 0 (
	echo Error activating virtualenv, exiting.
	echo exiting . . .
	pause
	exit 1
)

echo upgrading pip
python -m pip install -U pip
echo pip upgraded, upgrading setuptools
pip install --upgrade setuptools
echo setuptools upgraded

echo Installing all modules (Flask, Waitress, Pandas, Numpy, Pyteomics)
echo installing flask
pip install flask
IF %ERRORLEVEL% NEQ 0 (
	echo Error installing Flask. Installation failed.
	echo exiting . . . 
	pause
	exit 1
)

echo Flask installed successfully.


echo .
echo .
echo .
echo .

echo Installing Waitress.
pip install waitress
IF %ERRORLEVEL% NEQ 0 (
	echo error installing waitress. installation failed.
	echo exiting . . . 
	pause
	exit 1
)

echo Waitress installed successfully.


echo .
echo .
echo .
echo .

echo Installing Numpy.  This can take awhile, so please be patient.
TIMEOUT 5
pip install numpy -v
IF %ERRORLEVEL% NEQ 0 (
	echo error installing numpy. Installation failed
	echo exiting . . .
	pause
	exit 1
)

echo Numpy installed successfully.


echo .
echo .
echo .
echo .


echo Installing Pandas.
pip install pandas
IF %ERRORLEVEL% NEQ 0 (
	echo error installing pandas. Installation failed.
	echo exiting . . .
	pause
	exit 1
)
echo Pandas installed successfully.

echo .
echo .
echo .
echo .


echo Installing Pyteomics.
pip install pyteomics
IF %ERRORLEVEL% NEQ 0 (
	echo error installing pyteomics. Installation failed.
	echo exiting . . .
	pause
	exit 1
)

echo Pyteomics installed successfully.
echo .
echo .
echo .
echo .


echo Installing MatrixReal.
call cpan install Math::MatrixReal
IF %ERRORLEVEL% NEQ 0 (
	echo error installing MatrixReal. Installation failed.
	echo exiting . . .
	pause
	exit 1
)

echo MatrixReal installed successfully.
echo .
echo .
echo .
echo .

call deactivate


ECHO call GAILA_VENV\Scripts\activate > ..\start_gaila.bat
ECHO start python gaila_server.py >> ..\start_gaila.bat

echo GAILA installation successful.
echo Start the server by running start_gaila.bat


:END
pause