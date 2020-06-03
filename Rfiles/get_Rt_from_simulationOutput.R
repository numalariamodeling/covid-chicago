##============================================================
## R script to get R(t) from simulation outputs
##============================================================

#install.packages("devtools")
#library(devtools)
#install_github("annecori/EpiEstim", force = TRUE)

library(dplyr)
library(EpiEstim)




### Load  directories 


### Load simulation outputs
dat <- read.csv("C:/Users/mrung/Box/NU-malaria-team/projects/covid_chicago/NU_civis_outputs/20200603/csv/nu_il_baseline_20200602.csv")
#dat <- read.csv("C:/Users/mrung/Box/NU-malaria-team/projects/covid_chicago/NU_civis_outputs/20200603/trajectories/nu_il_baseline_20200602.csv")
disease_incidence_data <- dat %>% select(Number.of.Covid.19.new.infections) %>% rename(V1=Number.of.Covid.19.new.infections)

## Prepare 


### Run EpiEstim
#disease_incidence_data <- read.csv("DataS1.csv", header = FALSE)
serial_interval_data <- read.csv("DataS2.csv", header = FALSE)

serial_interval_data <- do.call("rbind", replicate(dim(disease_incidence_data)[1], serial_interval_data, simplify = FALSE))



names <- c("EL", "ER", "SL", "SR")
colnames(serial_interval_data) <- names
serial_interval_data <- as.data.frame(serial_interval_data)
disease_incidence_data <- as.data.frame(disease_incidence_data)

#Default config will estimate R on weekly sliding windows.
#To change this change the t_start and t_end arguments. 

#t_start=2:9, t_end=7:14,
R_estimate <- estimate_R(disease_incidence_data, si_data = serial_interval_data, method="si_from_data", 
                         config=list( n1 = 500, n2 = 100, seed = 1, 
                                mcmc_control=list(init.pars=NULL, burnin=3000, thin=10, seed=1), 
                                si_parametric_distr = "off1G"))


plot(R_estimate)

