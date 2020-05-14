### Description 

The emodl file contains all information that defines the mathematical model itself. 
For example, it defines the species, the transition rates, incubation time, daily recovery rate, and many other parameters specific to the disease being modeled. 
The model file is in EMODL format; the syntax and available parameters are described in [Model file syntax](https://idmod.org/docs/cms/model-file.html).


There are 4 types of models: 1) base, 2) age, 3) spatial, and 4) spatial-age. 
The base emodl file is edited per hand, whereas for the other types so called "emodl-generator" scripts are availabble. 
Note the term 'cobey' was removed from age and spatial file names to shorten the filename. 

The simple SEIR model was extended with additional compartments i.e. Hospitalized, detected and undetected cases, 
the model was further improved inspired from the compartmental model used at the University of Chicago and Sarah Cobeys group, hence the "cobey" term in the filename. 


| structure      | type                            | cms modifications        | intervention          | emodl name                                             |
|----------------|---------------------------------|--------------------------|-----------------------|--------------------------------------------------------|
| base           | master                          | none                     | continued SIP         | extendedmodel_cobey.emodl                              |
| base           | added intervention              | none                     | never SIP             | extendedmodel_cobey_noSIP.emodl                        |
| base           | added intervention              | none                     | immediate stop of SIP | extendedmodel_cobey_interventionStopy.emodl            |
| base           | added intervention              | none                     | gradual reopen        | extendedmodel_cobey_gradual_reopening.emodl            |
|                |                                 |                          |                       |                                                        |
| base           | master                          | testDelay                | continued SIP         | extendedmodeltestDelay_cobey.emodl                              |
| base           | added intervention              | testDelay                | never SIP             | extendedmodeltestDelay_cobey_noSIP.emodl                        |
| base           | added intervention              | testDelay                | immediate stop of SIP | extendedmodeltestDelay_cobey_interventionStopy.emodl            |
| base           | added intervention              | testDelay                | gradual reopen        | extendedmodeltestDelay_cobey_gradual_reopening.emodl            |
|                |                                 |                          |                       |                                                        |
| age-4          | homogeneous contacts            | none                     | continued SIP         | extendedmodel_age4_homogeneous.emodl                   |
| age-4          | all location contacts           | added contact matrix     | continued SIP         | extendedmodel_age4.emodl                               |
| age-4          | all location contacts           | added contact matrix     | never SIP             | extendedmodel_age4_neverSIP.emodl                      |
| age-4          | all location contacts           | added contact matrix     | immediate stop of SIP | extendedmodel_age4_interventionStop.emodl              |
| age-4          | all location contacts           | added contact matrix     | gradual reopen        | extendedmodel_age4_gradual_reopening.emodl             |
| age-4          | all location contacts           | added contact matrix     | gradual reopen        | extendedmodel_age4_contactTracing.emodl  
| age-4          | all location contacts           | age specific parameter   | continued SIP         | extendedmodel_age4_param.emodl                         |
|                |                                 |                          |                       |                                                        |
| age-8          | all location contacts           | added contact matrix     | continued SIP         | extendedmodel_age8.emodl                               |
| age-8          | all location contacts           | added contact matrix     | never SIP             | extendedmodel_age8_neverSIP.emodl                      |
| age-8          | all location contacts           | added contact matrix     | immediate stop of SIP | extendedmodel_age8_interventionStop.emodl              |
| age-8          | all location contacts           | added contact matrix     | gradual reopen        | extendedmodel_age8_gradual_reopening.emodl             |
| age-8          | all location contacts           | added contact matrix     | gradual reopen        | extendedmodel_age8_contactTracing.emodl 
| age-8          | all location contacts           | age specific parameter   | continued SIP         | extendedmodel_age8_param.emodl                         |
|                |                                 |                          |                       |                                                        |
| spatial-grp    | no migration                    | none                     | continued SIP         | extendedmodel_EMSgrp.emodl                            |
| spatial-grp    | no migration                    | none                     | never SIP             | extendedmodel_EMSgrp_neverSIP.emodl                   |
| spatial-grp    | no migration                    | none                     | immediate stop of SIP | extendedmodel_EMSgrp_interventionStop.emodl           |
| spatial-grp    | no migration                    | none                     | gradual reopen        | extendedmodel_EMSgrp_gradual_reopening.emodl          |
| spatial-grp    | no migration                    | none                     | gradual reopen + CT   | extendedmodel_EMSgrp_gradual_contactTracing.emodl  
|                |                                 |                          |                       |                                                        |
| spatial-grp    | no migration  				   | testDelay                | continued SIP         | extendedmodeltestDelay_EMSgrp.emodl                            |
| spatial-grp    | no migration  				   | testDelay                | never SIP             | extendedmodeltestDelay_EMSgrp_neverSIP.emodl                   |
| spatial-grp    | no migration  				   | testDelay                | immediate stop of SIP | extendedmodeltestDelay_EMSgrp_interventionStop.emodl           |
| spatial-grp    | no migration  				   | testDelay                | gradual reopen        | extendedmodeltestDelay_EMSgrp_gradual_reopening.emodl          |
| spatial-grp    | no migration  				   | testDelay                | gradual reopen + CT   | extendedmodeltestDelay_EMSgrp_gradual_contactTracing.emodl  
|                |                                 |                          |                       |                                                        |
| spatial-locale | no migration                    | none                     | continued SIP         | extendedmodel_cobey_localeZEMS.emodl                   |
| spatial-locale | no migration                    | none                     | never SIP             | extendedmodel_cobey_localeZEMS_neverSIP.emodl          |
| spatial-locale | no migration                    | none                     | immediate stop of SIP | extendedmodel_cobey_localeZEMS_interventionStop.emodl  |
| spatial-locale | no migration                    | none                     | gradual reopen        | extendedmodel_cobey_localeZEMS_gradual_reopening.emodl |
|                |                                 |                          |                       |                                                        |
| locale_age     | no migration  no contact matrix | none                     | continued SIP         | extendedmodel_cobey_locale_age_test.emodl              |


Note  for testDelay, the emodl name is extendedmodeltestDelay_xxxxx.emodl   
