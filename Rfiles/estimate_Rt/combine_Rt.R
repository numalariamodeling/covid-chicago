## ============================================================
## R script to combine Rt files 
## ============================================================

library(tidyverse)

f_loadAndCombine <- function(filedir, filename, identfier ){

  load(file.path(filedir, paste0(identfier[1],filename,".Rdata")))
  Rt_dat <- Rt_tempdat_All
  
  for (i in  identfier ) {
    load(file.path(filedir, paste0(i, filename, ".Rdata")))
    Rt_dat <- rbind(Rt_dat, Rt_tempdat_All)
    rm(Rt_tempdat_All)
  }
 return(Rt_dat) 
}


## Load directories and custom objects and functions
Location = "NUCLUSTER"
if(Location = "NUCLUSTER")) setwd("/home/mrm9534/gitrepos/covid-chicago/Rfiles/")
source("load_paths.R")

exp_name ="20200803_IL_baseline_reopeningScenarios"
fname = "_Rt_aggregated_scen_num"
   
Rt_dir <- file.path(simulation_output, exp_name,  "estimatedRt")

Rt_dat <- f_loadAndCombine(filedir=Rt_dir, filename=fname, identfier=c(1:11))

save(Rt_dat, file = file.path(Rt_dir, paste0("combined",fname, ".Rdata")))
write.csv(Rt_dat, file = file.path(Rt_dir, paste0("combined",fname, ".csv")), row.names = FALSE)
   

