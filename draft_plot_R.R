

library(tidyverse)
library(cowplot)
library(scales)
#library(deSolve)

username <- Sys.getenv("USERNAME")
project_dir <- file.path("C:/Users/", username, "/Box/NU-malaria-team/projects/covid_chicago")


## Chicago case data 
dat <- read.csv(file.path(project_dir, "Chicago_data/chicago_cases.csv")) 
dat <- dat %>% rename(Date = ï..Date) %>% 
  mutate(Date= as.Date(Date, format= "%m/%d/%y"))
dat$time <- seq(50, 50+nrow(dat)-1,1)


pred <- read.csv( file.path("C:/Users/", username, "Box/NU-malaria-team/projects/covid_chicago/cms_sim/sample_plots_extendedSEIR/trajectoriesDat_chicago_NHSmarketShare_v1.csv"))

summary(pred$detected)
ggplot()+ theme_cowplot() +
   geom_line(data=subset(pred, scen_num==1), aes(x=time, y=detected, group=interaction(sample_num, scen_num)))+
   geom_line(data=dat, aes(x=time, y=cumulative_cases_calc), col="deepskyblue2")+
   geom_point(data=dat, aes(x=time, y=cumulative_cases_calc), fill="white",col="deepskyblue2",size=3,shape=21)


