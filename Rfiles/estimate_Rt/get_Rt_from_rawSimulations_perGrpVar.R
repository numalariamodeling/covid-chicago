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

source("load_paths.R")
source("processing_helpers.R")
source("estimate_Rt/getRt_function.R")

exp_name = "20200803_IL_baseline_reopeningScenarios"
exp_dir <- file.path(simulation_output, exp_name)

Rt_dir <- file.path(simulation_output, exp_name, "estimatedRt")
if (!dir.exists(Rt_dir)) dir.create(Rt_dir)


### Load simulation outputs
tempdat <- read.csv(file.path(exp_dir, "trajectoriesDat.csv")) 


colnames(tempdat)[colnames(tempdat)== paste0( "infected_cumul_EMS.",ems)]  = "infected_cumul"
colnames(tempdat)[colnames(tempdat)== paste0( "infected_cumul_EMS-",ems)]  = "infected_cumul"
colnames(tempdat)

tempdat <- tempdat %>% 
  dplyr::mutate(
    startdate = as.Date(startdate),
    Date = as.Date(time + startdate),
  ) %>%
  dplyr::group_by(scen_num,reopening_multiplier_4) %>%
  dplyr::arrange(scen_num, reopening_multiplier_4, Date) %>%
  dplyr::mutate(new_infections = infected_cumul - lag(infected_cumul) )

tempdat <- tempdat %>% 
  dplyr::group_by(Date, reopening_multiplier_4) %>%
  dplyr::summarize(new_infections = mean(new_infections, na.rm=TRUE),
                   infected_cumul = mean(infected_cumul, na.rm=TRUE))


method <- "uncertain_si"
weekwindow=13

Rt_list <- list()
si_list <- list()
count=0
for (scen in unique(tempdat$reopening_multiplier_4)) {
  count = count + 1
  # scen = unique(tempdat$reopening_multiplier_4)[1]
  disease_incidence_data <- tempdat %>%
    dplyr::filter( reopening_multiplier_4 == scen) %>%
    dplyr::rename(I = new_infections) %>%
    dplyr::mutate(I = ifelse(I <0,0,I)) %>%
    dplyr::select(Date, I ,  infected_cumul) %>%
    dplyr::filter(!is.na(I))
  
  res <- getRt(disease_incidence_data, method=method, weekwindow=weekwindow)

  Rt_tempdat  <- res$R %>% mutate(region = ems, weekwindow=weekwindow )
  Rt_tempdat$reopening_multiplier_4 = scen
  
  if(count==1)Rt_tempdat_All  <- Rt_tempdat
  if(count!=1)Rt_tempdat_All  <- rbind(Rt_tempdat_All,Rt_tempdat)
  
  SI_tempdat  <- res$SI.Moments %>% mutate(region = ems, weekwindow=weekwindow )
  SI_tempdat$reopening_multiplier_4 = scen
  
  if(count==1)SI_tempdat_All  <- SI_tempdat
  if(count!=1)SI_tempdat_All  <- rbind(SI_tempdat_All,SI_tempdat) 
  
  rm(Rt_tempdat, SI_tempdat)
}

save(Rt_tempdat_All, file=file.path(Rt_dir, paste0(ems,"_Rt_aggregated_scen_num.Rdata")))



