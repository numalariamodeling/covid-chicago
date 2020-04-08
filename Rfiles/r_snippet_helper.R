
require(readxl)
require(tidyverse)

user_name = Sys.getenv("USERNAME")

if(user_name=="mrung") {
  data_dir = file.path("C:/Users",user_name,"Box/NU-malaria-team/projects/covid_chicago/emod_sim/age_contact_matrices")
  git_dir = file.path("C:/Users",user_name,"gitrepos/covid-chicago")
}


agegrp = c("grp4", "grp8")  # fix for now
age_groups4 = c("0to19","20to39","40to59","60to100")
age_groups8 = c("0to9" , "10to19" , "20to29", "30to39", "40to49", "50to59", "60to69", "70to100")

write_snippet <- function(agegrp, age_groups){
  txtfilename = paste0("datareplace_snippet_",agegrp,".txt")
  age_groupsNr = c(0:length(age_groups))[1:length(age_groups)]
  
  ### Write parameter snippet  (using mean only)
  sink(file=file.path(git_dir, "snippets", txtfilename)) 
  cat("# Age groups: ", age_groups8)
  cat(paste0("\ndata = data.replace('@speciesS_age" , age_groups, "@', str(df.speciesS_age", age_groups,"[sample_nr]))"))
  cat(paste0("\ndata = data.replace('@initialAs_age" , age_groups, "@', str(df.initialAs_age", age_groups,"[sample_nr]))"))
  
  cat(paste0("\ndf['speciesS_age" , age_groups, "'] = age_dic[", age_groupsNr,"][0]"))
  cat(paste0("\ndf['initialAs_age" , age_groups, "'] = age_dic[", age_groupsNr,"][1]"))
  
  
  
  sink()
  
  
}


write_snippet(agegrp[1], age_groups4)
write_snippet(agegrp[2], age_groups8)




