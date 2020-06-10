##============================================================
## R script to get R(t) from simulation outputs
##============================================================

#install.packages("devtools")
#library(devtools)
#install_github("annecori/EpiEstim", force = TRUE)

library(tidyverse)
library(EpiEstim)


source("load_paths.R")
setwd("estimate_Rt/from_simulations")

### Load simulation outputs
dat <- read.csv(file.path(project_path, "NU_civis_outputs/20200603/csv/nu_il_baseline_20200603.csv"))
summary(as.Date(dat$Date))


Rt_non_parametric_si_list <- list()
Rt_parametric_si_list <- list()
Rt_uncertain_si_list <- list()

for(region in unique(dat$geography_modeled)){
  # region = unique(dat$geography_modeled)[1]
  disease_incidence_data <- dat %>% filter(geography_modeled == region) %>%
  select(Number.of.Covid.19.new.infections) %>%
  rename(I=Number.of.Covid.19.new.infections)
  
#write.csv(disease_incidence_data,paste0(region,"disease_incidence_data.csv") , row.names = FALSE)


  ## check what si_distr to assume, or calculate from predictions, here using an example from the package
  si_distr <- c(0.000, 0.233, 0.359, 0.198, 0.103, 0.053, 0.027 ,0.014 ,0.007, 0.003, 0.002 ,0.001)
  res_non_parametric_si <- estimate_R(incid = disease_incidence_data$I, 
                    method = "non_parametric_si",
                    config = make_config(list(si_distr = si_distr)))
  
  pplot <- plot(res_non_parametric_si)
  ggsave(paste0(region, "_EpiEstim_default.pdf"),
         plot = pplot, path = file.path(getwd()), width = 6, height = 10, dpi = 300, device = "pdf"
  )
  
  
  res_parametric_si <- estimate_R(incid = disease_incidence_data$I, 
                                 method = "parametric_si",
                                  config = make_config(list(mean_si = 2.6, std_si = 1.5)))
  
  pplot <- plot(res_parametric_si)
  ggsave(paste0(region, "_EpiEstim_default_parametric_si.pdf"),
         plot = pplot, path = file.path(getwd()), width = 6, height = 10, dpi = 300, device = "pdf"
  )
  
  
  ## estimate the reproduction number (method "uncertain_si")
  res_uncertain_si <- estimate_R(disease_incidence_data$I, method = "uncertain_si",
                    config = make_config(list(
                      mean_si = 2.6, std_mean_si = 1,
                      min_mean_si = 1, max_mean_si = 4.2,
                      std_si = 1.5, std_std_si = 0.5,
                      min_std_si = 0.5, max_std_si = 2.5,
                      n1 = 100, n2 = 100)))
  
  pplot <- plot(res_uncertain_si)
  
  ggsave(paste0(region, "_EpiEstim_default_uncertain_si.pdf"),
         plot = pplot, path = file.path(getwd()), width = 6, height = 10, dpi = 300, device = "pdf"
  )
  
  
  Rt_non_parametric_si_list[[region]]  <-  res_non_parametric_si$R
  Rt_parametric_si_list[[region]]  <-  res_parametric_si$R
  Rt_uncertain_si_list[[region]] <-  res_uncertain_si$R
  
}





