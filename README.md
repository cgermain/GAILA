# GAILA - GPM and Isobaric Label Assistant


## FOR WINDOWS

### Prerequisites:
#### Download Python:
https://www.python.org/downloads/release/python-370/
Please make sure that Python is in your Windows PATH

#### Make sure Perl is installed (min v5.12):
https://strawberryperl.com/
Please make sure the cpan package manager is installed

#### Download Microsoft Visual C++ compiler: 
https://www.microsoft.com/en-us/download/details.aspx?id=44266
Then run the .msi installer to install


### INSTALLATION
Once the prerequisites are installed, download this folder by clicking the "download ZIP" button near the top-right of this page. Extract this zip file, and move the GAILA folder to a location of your choice. 

After unzipping, you should be able to set up the project by clicking on install.bat, located in the INSTALLATION folder. This file automatically checks for proper Python and Perl dependencies, as well as various Python packages (Flask, Numpy, Pandas, Pyteomics).


### TO RUN
The installation creates a file called start_gaila.bat. Double click this file to start the flask server. The server has to be running in order to access the browser based user interface. 

Open your web browser (Firefox or Chrome) and type localhost:5000 into the address bar. If the server is running correctly, you should see the user interface for our GPM and MGF-parsing scripts.

When you are done using GAILA, you can shut the server down by exiting the command prompt window that start_gaila.bat creates.

### If there are any issues with installation, the web interface, or the scripts themselves, please email germain@cabm.rutgers.edu.