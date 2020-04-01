library(tidyverse)
library(cowplot)

### Note the time period needs to be set once the starting date is fixed

#### Mortality estimates  per care location per age group
#care location: home
#care location: outpatient
#care location: med/surg
#care location: ICU
 
#mu home  =   deaths /  infected not hospitalized
#mu outpatient =   deaths /  undetected hospitalized path
#mu med/surg =   deaths / hospitalized detected
#mu ICU =   deaths / critical (detected and undetected) 


### Directories 
username = Sys.getenv("USERNAME")
simulation_output  = file.path("C:/Users/",username ,"/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/")

### Define experiment and load simulation outputs
#exp_name = "31032020_test_extendedModel_age_pop1000"
exp_name = "20200401_extendedModel_age_pop1000_v2"

files <- list.files(file.path(simulation_output, exp_name), pattern="trajectoresDat_withIncidence_age*", full.names =   T)

load_and_process_Dat <- function(file) {
      pred <- read.csv(file.path(file))
  
  #### Filter time, since using cumulative values, no aggregation needed
  pred <- pred %>% mutate(time = round(time,0)) %>%
                filter(time==31) %>% 
                pivot_longer(cols=-c(time ,sample_num ,scen_num)) %>%
                group_by(time,name)%>%
                summarize(value = mean(value)) %>%
                separate(name , into=c("channel","age"), sep="_age") %>%
                #filter(channel %in% c("symp_cumul","asymp_cumul","detected_cumul","hospitalized_cumul","hospitalized_cumul",,"deaths")) %>%
                pivot_wider(names_from = channel, values_from = value)  %>%
                mutate(infections_cumul = asymp_cumul + symp_cumul,
                       hospitalizations_cumul = hosp_det_cumul,
                       hosp_undet_cumul = hosp_cumul  - hosp_det_cumul,
                       #critical_cumul = crit_cumul - crit_det_cumul, 
                       #infections_home_cumul = symp_cumul - hospitalizations_cumul, 
                       infections_home_cumul = hosp_cumul - hosp_det_cumul, 
                       mortality_rate__overall = deaths/ infections_cumul,
                       mortality_rate__home = deaths/ infections_home_cumul,
                       mortality_rate__outpatient = deaths/ hosp_undet_cumul,
                       mortality_rate__med = deaths/ hosp_det_cumul,
                       mortality_rate__ICU = deaths/ crit_cumul,
                       ) 

  return(pred)
}


df.list <- lapply(files, load_and_process_Dat)
pred <- as.data.frame(do.call("rbind", df.list))
head(pred)

predOut <- pred %>% dplyr::select(age, mortality_rate__home, mortality_rate__med, mortality_rate__ICU, mortality_rate__outpatient) %>% 
          pivot_longer(cols=-age) %>% separate(name,  into=c("outcome","CareLocation"), sep="__") %>% 
          pivot_wider(names_from = outcome, values_from = value)


write.csv(predOut , file=file.path(simulation_output, "predicted_mortalityRates_TEST.csv"))
