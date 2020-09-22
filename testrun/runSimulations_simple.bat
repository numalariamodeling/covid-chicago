
@echo off
echo Welcome to the CMS test simulation, lets get started...
echo.
echo.

set /p EXE_DIR="Enter path to compartments.exe: "

@echo on
 echo start running simple model
"%EXE_DIR%\compartments.exe" -c "%CD%\simplemodel.cfg" -m "%CD%\simplemodel.emodl" >> "%CD%/log.txt"
 echo finished running simple model
 pause