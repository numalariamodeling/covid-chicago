

## Run a simple test using Compartmental Modelling Software (CMS)

If you have a compartments.exe
1) Go to the location of the compartments.exe and copy the file path (without the exe)
2) Run the simulation by double-clicking on runSimulations.bat (example simple SEIR model)
	- or runSimulations_covid_base.bat for a test run for the covid base model
    - or runSimulations_covid_age.bat for a test run for the covid age-stratified model 
	- or runSimulations_covid_locale.bat for a test run for the covid region-stratified model 
	- or runSimulations_covid_age-locale.bat for a test run for the covid age-region-stratified model 
3) A terminal window opens and asks for the path, paste the path you copied in 1
4) Once the simulation finished, you will see a trajectories.csv file and a log.txt file
5) Double-click on createPlot.bat to see the results

If you do not have a compartments.exe
0) follow the installation instruction on https://idmod.org/docs/cms/cms-installation.html then follow steps 1 to 5 above


