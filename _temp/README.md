# _temp

## In this folder the simulations are being generated and temporarily processed before moving to the destination folder on Box

## Simulation command examples

`cd covid-chicago`


### Running for all 11 regions in IL

`python runScenarios.py --scenario baseline -n test`

`python runScenarios.py --scenario vaccine -n test`

`python runScenarios.py --scenario bvariant_vaccine  -n test`

`python runScenarios.py --scenario bvariant -n test`

`python runScenarios.py --scenario rollback -n test`
`python runScenarios.py --scenario vaccine_rollback -n test`
`python runScenarios.py --scenario bvariant_vaccine_rollback -n test`

`python runScenarios.py --scenario reopen -n test`
`python runScenarios.py --scenario vaccine_reopen -n test`
`python runScenarios.py --scenario bvariant_vaccine_reopen -n test`



### Running single region

`python runScenarios.py -sr EMS_1 --scenario baseline -n test_reg1`

`python runScenarios.py -sr EMS_2 --scenario baseline -n test_reg2`

`python runScenarios.py -sr EMS_3 --scenario baseline -n test_reg3`

`python runScenarios.py -sr EMS_4 --scenario baseline -n test_reg4`

`python runScenarios.py -sr EMS_5 --scenario baseline -n test_reg5`

`python runScenarios.py -sr EMS_6 --scenario baseline -n test_reg6`

`python runScenarios.py -sr EMS_7 --scenario baseline -n test_reg7`

`python runScenarios.py -sr EMS_8 --scenario baseline -n test_reg8`

`python runScenarios.py -sr EMS_9 --scenario baseline -n test_reg9`

`python runScenarios.py -sr EMS_10 --scenario baseline -n test_reg10`

`python runScenarios.py -sr EMS_11 --scenario baseline -n test_reg11`



### Running multiple region 

Northcentral
`python runScenarios.py -sr EMS_1 EMS_2 --scenario baseline -n Northcentral`

Northeast
`python runScenarios.py -sr EMS_7 EMS_8 EMS_9 EMS_10 EMS_11 --scenario baseline -n Northeast`

Central
`python runScenarios.py -sr EMS_3 EMS_6 --scenario baseline -n Central`

Southern
`python runScenarios.py -sr EMS_4 EMS_5 --scenario baseline -n Southern`
 
Splitted
`python runScenarios.py -sr EMS_1 EMS_2 EMS_3 EMS_4 EMS_5 --scenario baseline -n EMS1to5`
`python runScenarios.py -sr EMS_6 EMS_7 EMS_8 EMS_9 EMS_10 EMS_11 --scenario baseline -n EMS6to11`


# Scenario choices
Detailed parameter description found [here](https://github.com/numalariamodeling/covid-chicago/tree/master/experiment_configs#experiment_config)
The selected scenario will automatically be included in the experiment name.

	baseline, rollback, reopen,rollback_reopen
	vaccine, rollback_vaccine, reopen_vaccine,rollback_reopen_vaccine
	bvariant, rollback_bvariant, reopen_bvariant,rollback_reopen_bvariant
	bvariant_vaccine, rollback_bvariant_vaccine, reopen_bvariant_vaccine, rollback_reopen_bvariant_vaccine
	 
	triggeredrollback, triggeredrollback_reopen
	triggeredrollback_vaccine,triggeredrollback_reopen_vaccine
	triggeredrollback_bvariant, triggeredrollback_reopen_bvariant
	triggeredrollback_bvariant_vaccine, triggeredrollback_reopen_bvariant_vaccine
