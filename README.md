# IDEAA - Isobaric Data Extractor and Annotator Assistant


## FOR WINDOWS

### Prerequisites:
#### Download Python:
https://www.python.org/downloads/release/python-370/
IDEAA expects Python to be installed at C:\Python37. If it is in another location, please change these references in /INSTALLATION/install.bat

#### Make sure Perl is installed (min v5.12):
http://www.activestate.com/activeperl/downloads
(Click "Download ActivePerl for Windows (64-bit, x64)" if you have 64 bit windows, and "Download ActivePerl for Windows (x86)" if you have 32 bit windows (all newer computers run 64 bit windows))

#### Download Microsoft Visual C++ compiler: 
https://www.microsoft.com/en-us/download/details.aspx?id=44266
Then run the .msi installer to install


### INSTALLATION
Once the prerequisites are downloaded, download this folder by clicking the "download ZIP" button near the top-right of this page. Unzip this zip file, and move the created folder to a location of your choice. 

After unzipping, you should be able to set up the project by clicking on install.bat, located in the INSTALLATION folder. This file automatically downloads dependencies, including pip (a python package manager), virtualEnv (a python dependency), as well as various python packages (flask, numpy, pandas, pyteomics).


### TO RUN
The installation creates a file called startup.bat. Double click this file to run the server. The server has to be running in order for the scripts to execute. When finished using it, you can shut the server down by exiting the command prompt window that startup.bat creates.

To use the interface, open your web browser (firefox or chrome) and type localhost:5000 into the URL bar. If the server is running correctly, you should see the User Interface for our GPM and MGF-parsing scripts.

### Please keep the summary file created after each run in the folder with the output files.  This will save time calculating total intensitites for future runs.

### PLAINCOUNT

This script counts proteins in MGF files that have been "plain parsed" using [IDEAA](https://github.com/cgermain/IDEAA).

## Installation on Windows

The /plaincount/plaincount.exe executable file was created with py2exe.  Microsoft's [Visual C++ runtime components](https://www.microsoft.com/en-us/download/details.aspx?id=29) might be required to use the application.

## Usage

GUI: Drag and drop a plain parsed file onto the plaincount.exe application icon.  Make sure to drag the file onto the icon itself and not in the command line window.

Command Line: python plaincount.py plain_parse_filename

### If there are any issues with installation, the web interface, or the scripts themselves, please email germain@cabm.rutgers.edu.
