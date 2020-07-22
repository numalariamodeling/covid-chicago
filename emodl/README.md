### Description 

The emodl file contains all information that defines the mathematical model itself. 
For example, it defines the species, the transition rates, incubation time, daily recovery rate, and many other parameters specific to the disease being modeled. 
The model file is in EMODL format; the syntax and available parameters are described in [Model file syntax](https://idmod.org/docs/cms/model-file.html).

There are 5 types of models: 1) base, 2) age, 3) spatial, 4) spatial-age, and 5) specified long-term care facility model (LTCF). 
The base emodl file is edited per hand, whereas for the other types so called "emodl-generator" scripts are availabble. 
The simple SEIR model was extended with additional compartments i.e. Hospitalized, detected and undetected cases, 
the model was extended with presymptomatic compartment in alignment with the compartmental model used at the University of Chicago and Prof Cobeys group, hence the "cobey" term in the filename. 

Main emodl file examples:

| structure      | type                            | cms modifications        | intervention          | emodl name                                             |
|----------------|---------------------------------|--------------------------|-----------------------|--------------------------------------------------------|
| base           | master                          | none                     | continued SIP         | extendedmodel_cobey.emodl                              |                       |
| base           | added intervention              | none                     | never SIP             | extendedmodel_cobey_noSIP.emodl                        |
| base           | added intervention              | none                     | immediate stop of SIP | extendedmodel_cobey_interventionStopy.emodl            |
| base           | added intervention              | none                     | gradual reopen        | extendedmodel_cobey_gradual_reopening.emodl            |
|                |                                 |                          |                       |                                                        |
|                |                                 |                          |                       |                                                        |
| age-8          | all location contact matrix     | age specific parameters   | continued SIP         | extendedmodel_age8.emodl                               |
| age-8          | all location contact matrix     | age specific parameters   | never SIP             | extendedmodel_age8_neverSIP.emodl                      |
| age-8          | all location contact matrix     | age specific parameters   | immediate stop of SIP | extendedmodel_age8_interventionStop.emodl              |
| age-8          | all location contact matrix     | age specific parameters   | gradual reopen        | extendedmodel_age8_gradual_reopening.emodl             |
| age-8          | all location contact matrix     | age specific parameters   | gradual reopen        | extendedmodel_age8_contactTracing.emodl 
|                |                                 |                          |                       |                                                        |
|                |                                 |                          |                       |                                                        |
| spatial        | no migration                    | none                     | continued SIP         | extendedmodel_EMS.emodl                   |
| spatial        | no migration                    | none                     | never SIP             | extendedmodel_EMS_neverSIP.emodl          |
| spatial        | no migration                    | none                     | immediate stop of SIP | extendedmodel_EMS_interventionStopadj.emodl  |
| spatial        | no migration                    | none                     | gradual reopen        | extendedmodel_EMS_gradual_reopening.emodl |
| spatial        | migration                       | none                     | gradual reopen        | extendedmodel_EMS_contact_tracing.emodl |
|                |                                 |                          |                       |                                                        |
| spatial        | migration                       | none                     | continued SIP         | extendedmodel_migration_EMS.emodl                   |
| spatial        | migration                       | none                     | never SIP             | extendedmodel_migration_EMS_neverSIP.emodl          |
| spatial        | migration                       | none                     | immediate stop of SIP | extendedmodel_migration_EMS_interventionStopadj.emodl  |
| spatial        | migration                       | none                     | gradual reopen        | extendedmodel_migration_EMS_gradual_reopening.emodl    |
| spatial        | migration                       | none                     | gradual reopen        | extendedmodel_migration_EMS_contact_tracing.emodl      |
|                |                                 |                          |                       |                                                        |
| locale_age     | migration and contact matrix    | none                     | continued SIP         | extendedmodel_agelocale_migration_scen3.emodl          |
|                |                                 |                          |                       |                                                        |
| ltcf           | no contact matrix               | group specific parameters| continued SIP         | extendedmodel_ltcf_age.emodl                           |
| ltcf           | contact matrix                  | group specific parameters| continued SIP         | extendedmodel_ltcf_homogeneous.emodl                   |
| ltcf           | contact matrix                  | group specific parameters| continued SIP         | extendedmodel_ltcf_age_testDelay.emodl                   |
