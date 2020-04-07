#==============================================================================
# R script to extract the aggregated contacts estimates between age groups
#==============================================================================
# Info: "Estimated age-mixing matrices for a US context were taken from the supplemental info from Prem, Cook, and Jit." 
# "Projecting social contact matrices in 152 countries using contact surveys and demographic data", Prem et al 2017
#==============================================================================

require(readxl)
require(tidyverse)

user_name = Sys.getenv("USERNAME")

if(user_name=="mrung") {
  data_dir = file.path("C:/Users",user_name,"Box/NU-malaria-team/projects/covid_chicago/emod_sim/age_contact_matrices")
  git_dir = file.path("C:/Users",user_name,"gitrepos/covid-chicago")
}


# As described in 20200318_EMODKingCountyCovidInterventions.docx
age_labels = c("0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39","40-44","45-49","50-54","55-59","60-64","65-69","70-74","75+")
age_groups = c("U5","age5to9","age20to64","age65")

#contacts_age_US <- read_excel("Desktop/contacts_age.xlsx", col_names = FALSE)
contacts_age <- read_excel(file.path(data_dir,"MUestimates_all_locations_2.xlsx"), sheet = "United States of America",col_names = FALSE)

contact_matrix <- data.frame()
#x ages
contact_matrix[1:4,1] <- rep(1,4)
contact_matrix[5:8,1] <- rep(2,4)
contact_matrix[9:12,1] <- rep(3,4)
contact_matrix[13:16,1] <- rep(4,4)
#y ages
contact_matrix[1:16,2] <- seq(1:4 )
#grab corresponding cols and row for each age interaction
#get mean, min, max
for (i in 1:16){
  if (i >=1 & i <= 4){columns=1}
  else if(i >= 5 & i <= 8){columns=2:4}
  else if(i >= 9 & i <= 12){columns=5:13}
  else if(i >= 13 & i <= 16){columns=14:16}
  if (i ==1 |i ==5|i == 9|i ==13 ){rows=1}
  else if(i ==2 |i ==6|i == 10|i ==14){rows=2:4}
  else if(i ==3 |i ==7|i == 11|i ==15){rows=5:13}
  else if (i ==4 |i ==8|i == 12|i ==16){rows=14:16}
  contact_matrix[i,3] <-mean(unlist(contacts_age[rows,columns]))
  contact_matrix[i,4] <- min(contacts_age[rows,columns])
  contact_matrix[i,5] <- max(contacts_age[rows,columns])
}
colnames(contact_matrix)[1:5] <- c("x","y","mean","lower_limit","upper_limit")

contact_matrix$age_x = factor(contact_matrix$x, levels=c(1:4), labels=age_groups)
contact_matrix$age_y = factor(contact_matrix$y, levels=c(1:4), labels=age_groups)

write_csv(contact_matrix,"contact_matrix.csv")


##==========================
### Add adjustments
##==========================

contact_matrix$age_xy = paste0(contact_matrix$x,"_", contact_matrix$y)

### Generate filter variable for symmetric age combinations
contact_matrix$symmetry=0
contact_matrix$symmetry[contact_matrix$age_xy %in% c("2_1", "3_1", "3_2", "4_1", "4_2", "4_3")] <- 1

### Same xy combination for symmetric contacts
contact_matrix$age_xy[contact_matrix$age_xy=="2_1"] <- "1_2"
contact_matrix$age_xy[contact_matrix$age_xy=="3_1"] <- "1_3"
contact_matrix$age_xy[contact_matrix$age_xy=="3_2"] <- "2_3"
contact_matrix$age_xy[contact_matrix$age_xy=="4_1"] <- "1_4"
contact_matrix$age_xy[contact_matrix$age_xy=="4_2"] <- "2_4"
contact_matrix$age_xy[contact_matrix$age_xy=="4_3"] <- "3_4"


### Take mean of symmetric contacts (i.e. should be same value for 1_2 and 2_1)
symmetry_means = contact_matrix %>% 
                        group_by(age_xy) %>% 
                        summarize_at(.vars=c("mean" ,"lower_limit" ,"upper_limit"),.funs="mean")
contact_matrix_adj = contact_matrix %>% 
                        select(x, age_xy,symmetry) %>% 
                        left_join(symmetry_means, by="age_xy")


### Rescale to 1s
contact_matrix_adj_scl = contact_matrix_adj %>% 
  filter(symmetry!=1) %>% 
  mutate(mean_scl = mean / sum(mean),
         #lower_limit_scl = lower_limit / sum(lower_limit),
         #upper_limit_scl = upper_limit / sum(upper_limit),
         age_x = factor(x, levels=seq(1:4),labels=age_groups ))  %>%
  select(age_xy, mean_scl)  #, lower_limit_scl, upper_limit_scl

contact_matrix_out = contact_matrix %>% 
                      select(x, age_xy,symmetry) %>% 
                      left_join(contact_matrix_adj_scl, by="age_xy")


### Write parameter snippet  (using mean only)
sink(file=file.path(git_dir, "snippets", "Ki_contact_snippet_grp4_v1.txt")) 
cat("# Age groups: ", age_groups)
cat(paste0("\ndf['sKi" , contact_matrix_out$age_xy, "'] = ", contact_matrix_out$mean_scl))
sink()


