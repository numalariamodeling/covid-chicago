### Rscrpt to zip the main files from multiple experiments into separate experiment subfolders for transferring them to Box.
### Note, the simulations and trajectories folder are not zipped and should be deleted from the _temp folder.

## Common pattern across experiments to transfer
stem = "contactTracingHS40$"

#temp_exp_dir <- file.path("/projects/p30781/covidproject/covid-chicago/_temp/")
#sim_output_dir <- file.path("/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_outputs/")


sim_output_dir = "/projects/p30781/covidproject/covid-chicago/_temp/"


exp_names <- list.files(sim_output_dir)[ grep(stem, list.files(sim_output_dir))]

foldertozipI <- file.path(sim_output_dir, stem)
if (!dir.exists(foldertozipI)) dir.create(foldertozipI)

for (exp_name in exp_names) {
  expdir <- file.path(sim_output_dir, exp_name)
  filestozip <- list.files(expdir, include.dirs = FALSE, all.files = FALSE, pattern = "[.]")
  foldertozipII <- file.path(foldertozipI, exp_name)
  if (!dir.exists(foldertozipII)) dir.create(foldertozipII)
  file.copy(file.path(expdir, filestozip), file.path(foldertozipII, filestozip))
}

setwd(sim_output_dir)
filestozipAll <- list.files(foldertozipI, recursive = T)
zip(zipfile = file.path(paste(stem, ".zip")), files = filestozipAll)

unlink(foldertozipI, recursive = TRUE, force = TRUE)
