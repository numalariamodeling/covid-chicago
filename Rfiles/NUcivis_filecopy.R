##=========================================
### Rscript to copy weekly results from simulation_output to NU_civis_outputs
##=========================================

#### R 
simdate = '20200805'
simulation_outputs <- file.path("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/")
project_dir <- 'C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/'
NUcivis_dir <- file.path(project_dir,'NU_civis_outputs')

##make dir
if(!dir.exists(file.path(NUcivis_dir,simdate))){dir.create(file.path(NUcivis_dir,simdate))
  dir.create(file.path(NUcivis_dir,simdate, 'plots'))
  dir.create(file.path(NUcivis_dir,simdate, 'csv'))
  dir.create(file.path(NUcivis_dir,simdate, 'trajectories'))
}
NUcivis_dir <- file.path(NUcivis_dir,simdate)


## Copy files
dirs <- list.dirs(simulation_outputs, recursive = FALSE)
dirs <- dirs[grep(simdate, dirs)]
nu_il_files <- list.files(dirs, pattern="nu_il_", recursive = TRUE, full.names = TRUE)
file.copy(nu_il_files, file.path(NUcivis_dir, 'csv'))


### Copy plots 
expnames <- gsub("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/","",dirs)

for(expname in expnames){
  
  if(!dir.exists(file.path(NUcivis_dir, "plots", expname))){
    dir.create(file.path(NUcivis_dir, "plots", expname))
  }
  
  t_png_files <- list.files(file.path(simulation_outputs,expname) , pattern="png", recursive = TRUE, full.names = TRUE)
  file.copy(t_png_files, file.path(NUcivis_dir, 'plots', expname))
  rm(t_png_files)
  
}


#### trajectories 
for(expname in expnames){
  
  t_csv_files <- list.files(file.path(simulation_outputs,expname) , 
                            pattern="trajectoriesDat.csv", recursive = TRUE, full.names = FALSE)
  
  t_csv_files_new = paste0("trajectoriesDat_",expname,".csv")
  file.copy(file.path(simulation_outputs,expname, t_csv_files), file.path(NUcivis_dir, 'trajectories', t_csv_files_new))
  rm(t_csv_files, t_csv_files_new)
}



###===============================================
### Run r-script for Rt estimation 
###===============================================
exp_scenarios =c("baseline","Aug15","Aug30","Sep15","Sep30")

for(exp_scenario in exp_scenarios){
  
  Location="LOCAL"
  source(file.path("C:/Users/mrm9534/gitrepos/covid-chicago/Rfiles/estimate_Rt/get_Rt_from_simulationOutput.R"))

}


##source(file.path("C:/Users/mrm9534/gitrepos/covid-chicago/Rfiles/estimate_Rt/Rt_plots_civis_results"))
