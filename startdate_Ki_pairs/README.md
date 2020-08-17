### Description 

The files here aim to generate simulations with varying startdate and Ki combinations per covid-region /EMS region to account for uncertainity when transmission started and at which intensity. 
[This](https://github.com/numalariamodeling/covid-chicago/blob/master/fit_Ki_Ki_red_start_date_all_ems.R) fitting process ([fit_Ki_Ki_red_start_date_all_ems.R](https://github.com/numalariamodeling/covid-chicago/blob/master/fit_Ki_Ki_red_start_date_all_ems.R))  results in multiple combinations of startdate and Ki for varying effect size estimates that were fitted to data.

The yaml file ([extendedmodel_200428_startdateKipair_template.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/startdate_Ki_pairs/extendedmodel_200428_startdateKipair_template.yaml)) corresponds to the [master yaml file](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml) with the exception of placeholders for startdates and Ki, that are replaced with the respective combinations when running [startdate_Ki_pairs.py](https://github.com/numalariamodeling/covid-chicago/blob/master/startdate_Ki_pairs/startdate_Ki_pairs.py)



Example combinations:

    'EMS_1': [2020-01-21, 2020-02-28]
    'EMS_2': [2020-01-24, 2020-02-29]
    'EMS_3': [2020-01-28, 2020-02-28]
    'EMS_4': [2020-01-20, 2020-02-29]
    'EMS_5': [2020-01-27, 2020-02-27]
    'EMS_6': [2020-01-28, 2020-02-28]
    'EMS_7': [2020-02-01, 2020-02-29]
    'EMS_8': [2020-02-01, 2020-02-26]
    'EMS_9': [2020-02-01, 2020-02-28]
    'EMS_10': [2020-02-03, 2020-02-22]
    'EMS_11': [2020-01-25, 2020-02-28]


   'EMS_1':
     np: linspace 
     function_kwargs: {'start': 0.25, 'stop': 0.583333333333333, 'num': 3}
   'EMS_2':
     np: linspace 
     function_kwargs: {'start': 0.28571428571428603, 'stop': 0.7142857142857142, 'num': 3}
   'EMS_3':
     np: linspace 
     function_kwargs: {'start': 0.28571428571428603, 'stop': 0.5714285714285711, 'num': 3}
   'EMS_4':
     np: linspace 
     function_kwargs: {'start': 0.28571428571428603, 'stop': 0.7142857142857142, 'num': 3}
   'EMS_5':
     np: linspace 
     function_kwargs: {'start': 0.28571428571428603, 'stop': 1.28571428571429, 'num': 3}
   'EMS_6':
     np: linspace 
     function_kwargs: {'start': 0.28571428571428603, 'stop': 0.5714285714285711, 'num': 3}
   'EMS_7':
     np: linspace 
     function_kwargs: {'start': 0.42857142857142894, 'stop': 1.0, 'num': 3}
   'EMS_8':
     np: linspace 
     function_kwargs: {'start': 0.42857142857142894, 'stop': 1.0, 'num': 3}
   'EMS_9':
     np: linspace 
     function_kwargs: {'start': 0.42857142857142894, 'stop': 1.0, 'num': 3}
   'EMS_10':
     np: linspace 
     function_kwargs: {'start': 0.42857142857142894, 'stop': 0.7142857142857142, 'num': 3}
   'EMS_11':
     np: linspace 
     function_kwargs: {'start': 0.42857142857142894, 'stop': 1.14285714285714, 'num': 3}
	 