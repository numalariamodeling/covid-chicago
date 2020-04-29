
## Description 
Note the following description was obtaiend from https://idmod.org/docs/cms/configuration-file.html and more details can be found there.

"While CMS does not require a configuration file, running a simulation without one uses default settings that will not produce scientifically useful results. 
As a stochastic model, you must run many realizations in a CMS simulation for statistically significant results. 
The configuration file uses JSON syntax and a .cfg file extension.
The table below shows the basic parameters used in a minimal configuration."
| Parameter | Data type | Default | Description                                                                                                                                                                                                          |   |
|-----------|-----------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| duration  | integer   | 100     | The number of time steps to run the realizations for; specified in   unitless time relevant to the timescales of the model. The values will   correspond to the units specified in the rates used in the model file. |   |
| runs      | integer   | 1       | The number of realizations to run for the simulation.                                                                                                                                                                |   |
| samples   | integer   | 100     | The number of samples of the various observables to take over the   duration of the simulation.       


## Solvers
For a description please go to https://idmod.org/docs/cms/solvers.html

### Approximate methods
- model_Tau.cfg and model.cfg  (default solver)
- model_B.cfg 
- model_RLeaping.cfg


### Spatial simulation methods
-  model_SSA.cfg

###  Exploratory methods
- model_RLeapingFast.cfg