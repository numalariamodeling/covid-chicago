

library(tidyverse)


trajectoriesDat <- read.csv("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/20200618_IL_EMS_test_base_test6/trajectoriesDat.csv")

# Ksym_DP ,Ksys_DP
trajectoriesDat$Date = trajectoriesDat$time + as.Date(trajectoriesDat$startdate)


dat <- trajectoriesDat %>% filter(Date >= '2020-06-10'  & Date <= '2020-06-12') %>%
                          select(infected_cumul_All, scen_num, Kl_D ,Ks_D ,Ksys_D ,Ksym_D ,Kh1_D ,Kh2_D ,
                                  Kh3_D ,Kr_m_D ,Kr_a_D ,fraction_symptomatic, fraction_severe, fraction_hospitalized ,
                                  time_to_infectious,time_to_symptoms, time_to_detection, time_to_hospitalization, time_to_critical,
                                 time_to_detection_As,time_to_detection_P, time_to_detection_Sym, time_to_detection_Sys ,
                                 recovery_time_asymp, recovery_time_mild, recovery_time_hosp) %>%
                        unique() %>% 
                        mutate(Kl = ( ( 1 - fraction_symptomatic ) / time_to_infectious) ,
                               Ksys = ( (fraction_symptomatic ) / time_to_infectious),
                               Ks = ( (fraction_severe ) / time_to_symptoms),
                               Ksym =  ( (1 -fraction_severe ) / time_to_symptoms),
                               Kr_a_D_T = 1/ (recovery_time_asymp - time_to_detection_As) )


dat_long <- dat %>% pivot_longer(cols=-c('infected_cumul_All','scen_num'))
  
ggplot(data=dat_long) + 
  geom_point(aes(x=value, y=infected_cumul_All)) + 
  geom_smooth(aes(x=value, y=infected_cumul_All) ,method="lm", se=FALSE) + 
  facet_wrap(~ name, scales="free_x")



dat %>% select(time_to_detection_Sym , Ksym_D ,Kr_m_D , recovery_time_mild)  %>% mutate( diff = recovery_time_mild -  time_to_detection_Sym, 
                                                                                         test = (1 / (time_to_detection_Sym )),
                                                                                         test1 = (1 / (recovery_time_mild -  time_to_detection_Sym )),
                                                                                         test2 = (1 / (recovery_time_mild )))

  