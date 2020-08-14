### Description 

The emodl file contains all information that defines the mathematical model itself. 
For example, it defines the species, the transition rates, incubation time, daily recovery rate, and many other parameters specific to the disease being modeled. 
The model file is in EMODL format; the syntax and available parameters are described in [Model file syntax](https://idmod.org/docs/cms/model-file.html).

There are 5 types of models: 1) base, 2) age, 3) spatial, 4) spatial-age, and 5) specified long-term care facility model (LTCF). 
Different "emodl-generators" are available to generate an emodl. 


Naming conventions 
1) compartmental model type 'extendedmodel' 
2) grp specification if any '_EMS'  
3) time event scenario specification '_dAsP'

Emodl examples:

| structure      | type                            | cms modifications        | intervention          | emodl name                                             |
|----------------|---------------------------------|--------------------------|-----------------------|--------------------------------------------------------|
| base           | master                          | none                     | continued SIP         | extendedmodel_cobey.emodl                              |                       |
| base           | added intervention              | none                     | never SIP             | extendedmodel_cobey_noSIP.emodl                        |
| base           | added intervention              | none                     | immediate stop of SIP | extendedmodel_cobey_interventionStopy.emodl            |
| base           | added intervention              | none                     | gradual reopen        | extendedmodel_cobey_gradual_reopening.emodl            |
|                |                                 |                          |                       |                                                        |
| age-8          | all location contact matrix     | age specific parameters   | continued SIP         | extendedmodel_age8.emodl                               |
| age-8          | all location contact matrix     | age specific parameters   | never SIP             | extendedmodel_age8_neverSIP.emodl                      |
| age-8          | all location contact matrix     | age specific parameters   | ...                  | optionally add interventions as required            |
|                |                                 |                          |                       |                                                        |
|                |                                 |                          |                       |                                                        |
| spatial        | no migration                    | none                     | continued SIP         | extendedmodel_EMS.emodl                   |
| spatial        | no migration                    | none                     | never SIP             | extendedmodel_EMS_neverSIP.emodl          |
| spatial        | no migration                    | none                     | immediate stop of SIP | extendedmodel_EMS_interventionStopadj.emodl  |
| spatial        | no migration                    | none                     | gradual reopen        | extendedmodel_EMS_gradual_reopening.emodl |
|                |                                 |                          |                       |                                                        |
| spatial        | migration                       | none                     | continued SIP         | extendedmodel_migration_EMS.emodl                   |
| spatial        | migration                       | none                     | never SIP             | extendedmodel_migration_EMS_neverSIP.emodl          |
| spatial        | migration                       | none                     | immediate stop of SIP | extendedmodel_migration_EMS_interventionStopadj.emodl  |
| spatial        | migration                       | none                     | ...       | analougous to the model without migration    |
|                |                                 |                          |                       |                                                        |
| locale_age     | migration and contact matrix    | none                     | continued SIP         | extendedmodel_agelocale_migration_scen3.emodl          |
|                |                                 |                          |                       |                                                        |
| ltcf           | no contact matrix               | group specific parameters| continued SIP         | extendedmodel_ltcf_age.emodl                           |
| ltcf           | no contact matrix               | group specific parameters| continued SIP         | extendedmodel_ltcf_homogeneous.emodl                   |
| ltcf           | contact matrix                  | group specific parameters| continued SIP         | extendedmodel_ltcf_age_testDelay.emodl                   |
