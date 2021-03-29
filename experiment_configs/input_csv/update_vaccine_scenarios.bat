echo 
echo %CD%
cd ..
cd ..
echo %CD%


python data_processing/vaccinations_by_age.py
python data_processing/vaccinations_by_covidregion.py

R --vanilla -f  "Rfiles/vaccine_scenarios.R"
R --vanilla -f  "Rfiles/vaccine_scenario_fracSevere.R"

pause