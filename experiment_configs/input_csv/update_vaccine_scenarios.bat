echo 
echo %CD%
cd ..
cd ..
echo %CD%

cd data_processing
python vaccinations_by_age.py
python vaccinations_by_covidregion.py

cd ..
cd Rfiles
R --vanilla -f  "vaccine_scenarios.R"
R --vanilla -f  "vaccine_scenario_fracSevere.R"

pause