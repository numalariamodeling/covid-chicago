# ==============================================================================
# R script to extract the aggregated contacts estimates between age groups
# ==============================================================================
# Info: "Estimated age-mixing matrices for a US context were taken from the supplemental info from Prem, Cook, and Jit."
# "Projecting social contact matrices in 152 countries using contact surveys and demographic data", Prem et al 2017
# ==============================================================================

require(readxl)
require(tidyverse)

user_name <- Sys.getenv("USERNAME")

if (user_name == "mrung") {
  data_dir <- file.path("C:/Users", user_name, "Box/NU-malaria-team/projects/covid_chicago/emod_sim/age_contact_matrices")
  git_dir <- file.path("C:/Users", user_name, "gitrepos/covid-chicago")
  input_dir <- file.path("C:/Users", user_name, "Box/NU-malaria-team/projects/covid_chicago/cms_sim/inputs/contact_matrices/")
}


### add population 

agegrps <- c("grp4", "grp8")
contactlocations <- c("locations_all", "home", "school", "work", "locations_other")


for (agegrp in agegrps) {
  for (contactlocation in contactlocations) {
    age_groups4 <- c("0to19", "20to39", "40to59", "60to100")
    age_groups8 <- c("0to9", "10to19", "20to29", "30to39", "40to49", "50to59", "60to69", "70to100")

    if (agegrp == "grp4") age_groups <- age_groups4
    if (agegrp == "grp8") age_groups <- age_groups8


    txtfilename <- paste0("Ki_contact_snippet_", contactlocation, "_", agegrp, ".txt")
    csvfilename <- paste0("contact_matrix_", contactlocation, "_", agegrp, ".csv")

    ### Read in contact matrix
    contact_matrix <- read_csv(file.path(input_dir, csvfilename)) %>% as.data.frame()

    colnames(contact_matrix)[2:length(colnames(contact_matrix))] <- c(1:length(age_groups))
    contact_matrix$x <- c(1:length(age_groups))


    contact_matrix <- contact_matrix %>%
      dplyr::select(-row_age_group) %>%
      pivot_longer(cols = -c(x), names_to = "y") %>%
      dplyr::rename(mean = value)

    contact_matrix$age_xy <- paste0(contact_matrix$x, "_", contact_matrix$y)


    ### Generate filter variable for symmetric age combinations
    contact_matrix$symmetry <- 0
    contact_matrix$age_xy_orig <- contact_matrix$age_xy

    if (agegrp == "grp4") {
      contact_matrix$symmetry[contact_matrix$age_xy %in% c("2_1", "3_1", "3_2", "4_1", "4_2", "4_3")] <- 1

      ### Same xy combination for symmetric contacts
      contact_matrix$age_xy[contact_matrix$age_xy == "2_1"] <- "1_2"
      contact_matrix$age_xy[contact_matrix$age_xy == "3_1"] <- "1_3"
      contact_matrix$age_xy[contact_matrix$age_xy == "3_2"] <- "2_3"
      contact_matrix$age_xy[contact_matrix$age_xy == "4_1"] <- "1_4"
      contact_matrix$age_xy[contact_matrix$age_xy == "4_2"] <- "2_4"
      contact_matrix$age_xy[contact_matrix$age_xy == "4_3"] <- "3_4"
    }
    if (agegrp == "grp8") {
      contact_matrix$symmetry[contact_matrix$age_xy %in% c(
        "2_1",
        "3_1", "3_2",
        "4_1", "4_2", "4_3",
        "5_1", "5_2", "5_3", "5_4",
        "6_1", "6_2", "6_3", "6_4", "6_5",
        "7_1", "7_2", "7_3", "7_4", "7_5", "7_6",
        "8_1", "8_2", "8_3", "8_4", "8_5", "8_6"
      )] <- 1

      ### Same xy combination for symmetric contacts

      contact_matrix$age_xy_orig <- contact_matrix$age_xy
      contact_matrix$age_xy[contact_matrix$age_xy == "2_1"] <- "1_2"
      contact_matrix$age_xy[contact_matrix$age_xy == "3_1"] <- "1_3"
      contact_matrix$age_xy[contact_matrix$age_xy == "3_2"] <- "2_3"
      contact_matrix$age_xy[contact_matrix$age_xy == "4_1"] <- "1_4"
      contact_matrix$age_xy[contact_matrix$age_xy == "4_2"] <- "2_4"
      contact_matrix$age_xy[contact_matrix$age_xy == "4_3"] <- "3_4"

      contact_matrix$age_xy[contact_matrix$age_xy == "5_1"] <- "1_5"
      contact_matrix$age_xy[contact_matrix$age_xy == "5_2"] <- "2_5"
      contact_matrix$age_xy[contact_matrix$age_xy == "5_3"] <- "3_5"
      contact_matrix$age_xy[contact_matrix$age_xy == "5_4"] <- "4_5"

      contact_matrix$age_xy[contact_matrix$age_xy == "6_1"] <- "1_6"
      contact_matrix$age_xy[contact_matrix$age_xy == "6_2"] <- "2_6"
      contact_matrix$age_xy[contact_matrix$age_xy == "6_3"] <- "3_6"
      contact_matrix$age_xy[contact_matrix$age_xy == "6_4"] <- "4_6"
      contact_matrix$age_xy[contact_matrix$age_xy == "6_5"] <- "5_6"

      contact_matrix$age_xy[contact_matrix$age_xy == "7_1"] <- "1_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "7_2"] <- "2_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "7_3"] <- "3_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "7_4"] <- "4_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "7_5"] <- "5_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "7_6"] <- "6_7"

      contact_matrix$age_xy[contact_matrix$age_xy == "8_1"] <- "1_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "8_2"] <- "2_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "8_3"] <- "3_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "8_4"] <- "4_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "8_5"] <- "5_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "8_6"] <- "6_7"
      contact_matrix$age_xy[contact_matrix$age_xy == "8_6"] <- "6_7"
    }


    ### Take mean of symmetric contacts (i.e. should be same value for 1_2 and 2_1)
    symmetry_means <- contact_matrix %>%
      group_by(age_xy) %>%
      summarize_at(.vars = c("mean"), .funs = "mean")


    contact_matrix_adj <- contact_matrix %>%
      select(x, y,age_xy, symmetry) %>%
      left_join(symmetry_means, by = "age_xy") %>%
      select(x, y, mean) %>%
      mutate(y=paste0("y",y))%>%
      pivot_wider( values_from = mean, names_from = y) %>% 
      unite("pintcol", -x, remove = T, sep=", ")
    
  
    ### Leave contact matrix as it is, normalization and population weighting is done in cms, or separate python script


    ### Write parameter snippet  (using mean only)
    sink(file = file.path(git_dir, "age_model/age_contact", txtfilename))
    cat("# Age groups: ", age_groups)
    cat("C: \nmatrix:  # Unnormalized contact matrix ")
    cat(paste0("\n- [", contact_matrix_adj$pintcol, "]"))
    sink()
    
  }
}