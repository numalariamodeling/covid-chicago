
@echo off
echo Welcome to the CMS test simulation, lets get started...
echo.
echo.

set /p EXE_DIR="Enter path to compartments.exe: "

@echo on
 echo start running simple model
"%EXE_DIR%\compartments.exe" -c "C:\Users\HP1\Documents\covid-chicago\_temp\20200922_IL_ms_testrun\simulations\model_2.cfg" -m "C:\Users\HP1\Documents\covid-chicago\_temp\20200922_IL_ms_testrun\simulations\simulation_2.emodl"
 echo finished running simple model
 pause