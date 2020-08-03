## ============================================================
## R script to get R(t) from simulation outputs
## ============================================================

# install.packages("devtools")
# library(devtools)
# install_github("annecori/EpiEstim", force = TRUE)
library(tidyverse)
library(EpiEstim)

runinBatchMode = TRUE


if(runinBatchMode){
  cmd_agrs <- commandArgs()
  length(cmd_agrs)
  ems <- cmd_agrs[length(cmd_agrs)]
  
  task_id <- Sys.getenv("SLURM_ARRAY_TASK_ID")
  print(task_id)
  ems <- task_id
} else {
  ems <- "11"
}


print(ems)

setwd("/home/mrm9534/gitrepos/covid-chicago/Rfiles/")
source("/home/mrm9534/gitrepos/covid-chicago/Rfiles/load_paths.R")
source("/home/mrm9534/gitrepos/covid-chicago/Rfiles/processing_helpers.R")

exp_name = "20200731_IL_reopen_contactTracing"
exp_dir <- file.path(simulation_output, exp_name)

Rt_dir <- file.path(simulation_output, exp_name, "estimatedRt")
if (!dir.exists(Rt_dir)) dir.create(Rt_dir)


### Load simulation outputs
tempdat <- read.csv(file.path(exp_dir, "trajectoriesDat.csv")) %>% 
  dplyr::mutate(
  startdate = as.Date(startdate),
  Date = as.Date(time + startdate)
)


colnames(tempdat)[colnames(tempdat)== paste0( "infected_cumul_EMS.",ems)]  = "infected_cumul"
colnames(tempdat)[colnames(tempdat)== paste0( "infected_cumul_EMS-",ems)]  = "infected_cumul"
colnames(tempdat)

tempdat <- tempdat %>% 
  dplyr::mutate(
    startdate = as.Date(startdate),
    Date = as.Date(time + startdate),
  ) %>%
  dplyr::group_by( scen_num) %>%
  dplyr::arrange( scen_num, Date) %>%
  dplyr::mutate(region = ems, new_infections = infected_cumul - lag(infected_cumul) )


method <- "uncertain_si"
Rt_list <- list()
si_list <- list()
count=0
for (scen in unique(tempdat$scen_num)) {
  count = count + 1
  # scen = unique(dat$scen_num)[1]
  disease_incidence_data <- tempdat %>%
    dplyr::filter(region == ems ,   scen_num == scen) %>%
    dplyr::rename(I = new_infections) %>%
    dplyr::mutate(I = ifelse(I <0,0,I)) %>%
    dplyr::select(Date, I ,  infected_cumul) %>%
    dplyr::filter(!is.na(I))
  
  ## check what si_distr to assume, or calculate from predictions, here using an example from the package
  if(method=="non_parametric_si"){  
    si_distr <- c(0.000, 0.233, 0.359, 0.198, 0.103, 0.053, 0.027 ,0.014 ,0.007, 0.003, 0.002 ,0.001)
    res <- estimate_R(incid = disease_incidence_data$I,
                      method = "non_parametric_si",
                      config = make_config(list(si_distr = si_distr)))
    
  }
  
  ### use parametric_si
  if(method=="parametric_si"){  
    res <- estimate_R(incid = disease_incidence_data$I,
                      method = "parametric_si",
                      config = make_config(list(mean_si = 2.6, std_si = 1.5)))
  }
  
  ## biweekly sliding
  t_start <- seq(2, nrow(disease_incidence_data)-13)   
  t_end <- t_start + 13  
  
  ## estimate the reproduction number (method "uncertain_si")
  if(method=="uncertain_si"){
    res <- estimate_R(disease_incidence_data$I,
                      method = "uncertain_si",
                      config = make_config(list(
                        t_start = t_start, 
                        t_end = t_end,
                        mean_si = 4.6, std_mean_si = 1,
                        min_mean_si = 1, max_mean_si = 7.5,
                        std_si = 1.5, std_std_si = 0.5,
                        min_std_si = 0.5, max_std_si = 2.5,
                        n1 = 100, n2 = 100
                      ))
    )
  }
  

  Rt_tempdat  <- res$R %>% mutate(region = ems)
  Rt_tempdat$scen_num = scen
  
  if(count==1)Rt_tempdat_All  <- Rt_tempdat
  if(count!=1)Rt_tempdat_All  <- rbind(Rt_tempdat_All,Rt_tempdat)
  
  SI_tempdat  <- res$SI.Moments %>% mutate(region = ems)
  SI_tempdat$scen_num = scen
  
  if(count==1)SI_tempdat_All  <- SI_tempdat
  if(count!=1)SI_tempdat_All  <- rbind(SI_tempdat_All,SI_tempdat) 
  
  rm(Rt_tempdat, SI_tempdat)
}

save(Rt_tempdat_All, file=file.path(Rt_dir, paste0(ems,"_temp_Rt_tempdat_All.Rdata")))



