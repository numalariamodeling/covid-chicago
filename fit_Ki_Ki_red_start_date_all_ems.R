
# This script takes hospital data from various EMS regions of Illinois, and compares
## them to simulations where we varied the transmission parameter (Ki), the amount
# that Ki was reduced during shelter in place, and the start date of the epidemic
# (10 asymptomatic individuals) for each EMS region

# This script assumes that inside simulation output, there is a file
# called EMS_X, where X is a given ems region.
# It assumes that inside that file is a sheet title trajectoriesDat.csv
# It also assumes that in the "data" folder int he "covid_chicago" folder on box
# There are files titled "emresource_by_region.csv", "200522_jg_admission_date_ems.csv",
# And "200522_jg_deceased_date_ems.csv".
# The "library(here) call sets the working directoty to be wherever this file lives.
# For me it lived inside the covid_chicago file in Box (unsynced). If youres lives in git,
# put in a call to set the working directory to the covid_chicago folder on box.
# Line 233- change working directory to where you want results saved.

## set working directory to R.project location
library(here)
library(ggplot2)
library(tidyverse)


username = Sys.getenv("USERNAME")
if(username=="mrung"){
  Box_dir = file.path("C:/Users/mrung/Box/NU-malaria-team")
  simulation_output_dir = file.path(Box_dir,"projects/covid_chicago/cms_sim/simulation_output/")
  data_dir = file.path(Box_dir,"data/")
  out_dir =  file.path(Box_dir,"projects/covid_chicago/parameter_estimates_by_EMS/v2/")
}else{
  Box_dir <- getwd()
  simulation_output_dir <- file.path(Box_dir,'covid_chicago','cms_sim')
  data_dir = file.path(Box_dir)
  out_dir =  file.path(Box_dir,'covid_chicago',"parameter_estimates_by_EMS/v2/")
}


simdate = "20200525"

## Read in simulations, put in list
sim_ems1 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_1_fit_test1/trajectoriesDat.csv"))
sim_ems2 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_2_fit_test1/trajectoriesDat.csv"))
sim_ems3 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_3_fit_test1/trajectoriesDat.csv"))
sim_ems4 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_4_fit_test1/trajectoriesDat.csv"))
sim_ems5 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_5_fit_test1/trajectoriesDat.csv"))
sim_ems6 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_6_fit_test1/trajectoriesDat.csv"))
sim_ems7 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_7_fit_test1/trajectoriesDat.csv"))
sim_ems8 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_8_fit_test1/trajectoriesDat.csv"))
sim_ems9 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_9_fit_test1/trajectoriesDat.csv"))
sim_ems10 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_10_fit_test1/trajectoriesDat.csv"))
sim_ems11 <- read.csv(file.path(simulation_output_dir,"forFitting/",simdate,"_EMS_11_fit_test1/trajectoriesDat.csv"))


simulationslist <- list(sim_ems1, sim_ems2, sim_ems3, sim_ems4, sim_ems5, sim_ems6, sim_ems7, sim_ems8, sim_ems9, sim_ems10, sim_ems11)
# simulationslist <- list(sim_ems2)

# read in hospital data
hosp_data <- read.csv(file.path(data_dir,"covid_IDPH/Corona virus reports/emresource_by_region.csv"))

# Replace NA values with zeros (blank in raw data sheet)
hosp_data[is.na(hosp_data)] <- 0

# Dates in sheet currently as factor, make as dat
hosp_data$date_of_extract <- as.Date(hosp_data$date_of_extract)

## Separate hospital data by EMS, put in list
hosp_data_ems1 <- hosp_data[which(hosp_data$region == 1), ]
hosp_data_ems2 <- hosp_data[which(hosp_data$region == 2), ]
hosp_data_ems3 <- hosp_data[which(hosp_data$region == 3), ]
hosp_data_ems4 <- hosp_data[which(hosp_data$region == 4), ]
hosp_data_ems5 <- hosp_data[which(hosp_data$region == 5), ]
hosp_data_ems6 <- hosp_data[which(hosp_data$region == 6), ]
hosp_data_ems7 <- hosp_data[which(hosp_data$region == 7), ]
hosp_data_ems8 <- hosp_data[which(hosp_data$region == 8), ]
hosp_data_ems9 <- hosp_data[which(hosp_data$region == 9), ]
hosp_data_ems10 <- hosp_data[which(hosp_data$region == 10), ]
hosp_data_ems11 <- hosp_data[which(hosp_data$region == 11), ]

hosp_list <- list(hosp_data_ems1,hosp_data_ems2,hosp_data_ems3, hosp_data_ems4, hosp_data_ems5, hosp_data_ems6, hosp_data_ems7, hosp_data_ems8, hosp_data_ems9, hosp_data_ems10, hosp_data_ems11)

# Read in by line hospital admissions data
pre_hosp_adm_data <- read.csv(file.path(data_dir, "covid_IDPH", "Cleaned Data", "200522_jg_admission_date_ems.csv"))


# Make date column as date
pre_hosp_adm_data <- pre_hosp_adm_data %>%
  mutate(date = as.Date(date, "%Y-%m-%d"))

# Divide by EMS and put in list
pre_hosp_adm_data_ems1 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 1), ]
pre_hosp_adm_data_ems2 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 2), ]
pre_hosp_adm_data_ems3 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 3), ]
pre_hosp_adm_data_ems4 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 4), ]
pre_hosp_adm_data_ems5 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 5), ]
pre_hosp_adm_data_ems6 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 6), ]
pre_hosp_adm_data_ems7 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 7), ]
pre_hosp_adm_data_ems8 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 8), ]
pre_hosp_adm_data_ems9 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 9), ]
pre_hosp_adm_data_ems10 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 10), ]
pre_hosp_adm_data_ems11 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 11), ]

pre_hosp_adm_list <- list(
  pre_hosp_adm_data_ems1, pre_hosp_adm_data_ems2,
  pre_hosp_adm_data_ems3, pre_hosp_adm_data_ems4,
  pre_hosp_adm_data_ems5, pre_hosp_adm_data_ems6,
  pre_hosp_adm_data_ems7, pre_hosp_adm_data_ems8,
  pre_hosp_adm_data_ems9, pre_hosp_adm_data_ems10,
  pre_hosp_adm_data_ems11
)
# pre_hosp_adm_list <- list(pre_hosp_adm_data_ems2)

# Read in by line hospital death data
pre_hosp_det_data <- read.csv(file.path(data_dir, "covid_IDPH", "Cleaned Data", "200522_jg_deceased_date_ems.csv"))
# Make date column as dat
pre_hosp_det_data <- pre_hosp_det_data %>%
  mutate(date = as.Date(date, "%Y-%m-%d"))

# Divide by EMS and put in list
pre_hosp_det_data_ems1 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 1), ]
pre_hosp_det_data_ems2 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 2), ]
pre_hosp_det_data_ems3 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 3), ]
pre_hosp_det_data_ems4 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 4), ]
pre_hosp_det_data_ems5 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 5), ]
pre_hosp_det_data_ems6 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 6), ]
pre_hosp_det_data_ems7 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 7), ]
pre_hosp_det_data_ems8 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 8), ]
pre_hosp_det_data_ems9 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 9), ]
pre_hosp_det_data_ems10 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 10), ]
pre_hosp_det_data_ems11 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 11), ]

pre_hosp_det_list <- list(
  pre_hosp_det_data_ems1, pre_hosp_det_data_ems2,
  pre_hosp_det_data_ems3, pre_hosp_det_data_ems4,
  pre_hosp_det_data_ems5, pre_hosp_det_data_ems6,
  pre_hosp_det_data_ems7, pre_hosp_det_data_ems8,
  pre_hosp_det_data_ems9, pre_hosp_det_data_ems10,
  pre_hosp_det_data_ems11
)


## loop begin over EMS regions
use_values_list <- list()
for (i in 1:11) {

  # OK, let's prepare the simulation sheet
  sim_ems <- simulationslist[[i]]
  sim_ems <- na.omit(sim_ems)


  # In the simulations, add a colum for deaths each day rather than cumulative deaths
  sim_ems$death_det_24hr <- 0
  sim_ems$death_det_24hr[2:length(sim_ems$death_det_24hr)] <- sim_ems$death_det_cumul[2:length(sim_ems$death_det_24hr)] - sim_ems$death_det_cumul[1:(length(sim_ems$death_det_24hr) - 1)]
  for (x in 1:length(sim_ems$death_det_24hr)) {
    if (sim_ems$time[x] == 0) {
      sim_ems$death_det_24hr[x] <- 0
    }
  }

  # Also add a column for new detected symptomatic each day
  sim_ems$new_det <- 0
  sim_ems$new_det[2:length(sim_ems$new_det)] <- (sim_ems$symp_mild_det_cumul[2:length(sim_ems$symp_mild_det_cumul)] + sim_ems$symp_severe_det_cumul[2:length(sim_ems$symp_severe_det_cumul)]) -
    (sim_ems$symp_mild_det_cumul[1:(length(sim_ems$symp_mild_det_cumul) - 1)] + sim_ems$symp_severe_det_cumul[1:(length(sim_ems$symp_severe_det_cumul) - 1)])
  for (x in 1:length(sim_ems$new_det)) {
    if (sim_ems$time[x] == 0) {
      sim_ems$new_det[x] <- 0
    }
  }

  # We need to match simulation dates with real world dates.
  # simulation dates aren't integers, so round them.
  sim_ems$time <- floor(sim_ems$time)
  table(sim_ems$startdate)

  ## get EMS specific hosp_data
  hosp_data_ems <- hosp_list[[i]]

  ## get EMS specific admissions data
  pre_hosp_adm_data_ems <- pre_hosp_adm_list[[i]]

  # Fill in dates that are missing with 0's
  pre_hosp_adm_data_ems <- pre_hosp_adm_data_ems %>%
    complete(date = seq.Date(min(pre_hosp_adm_data_ems$date), max(pre_hosp_adm_data_ems$date), by = "day"))
  pre_hosp_adm_data_ems$EMS <- i
  pre_hosp_adm_data_ems[is.na(pre_hosp_adm_data_ems)] <- 0

  ## get EMS specific death data
  pre_hosp_det_data_ems <- pre_hosp_det_list[[i]]

  # Fill in dates that are missing with 0's
  pre_hosp_det_data_ems <- pre_hosp_det_data_ems %>%
    complete(date = seq.Date(min(pre_hosp_det_data_ems$date), max(pre_hosp_det_data_ems$date), by = "day"))
  pre_hosp_det_data_ems$EMS <- i
  pre_hosp_det_data_ems[is.na(pre_hosp_det_data_ems)] <- 0


  ## get a list of all scenario numbers run for this EMS
  scens <- unique(sim_ems$scen_num)

  # create data.frame to hold likelihood results
  ems_output <- matrix(0, length(scens), 4)
  ems_output <- as.data.frame(ems_output)
  colnames(ems_output) <- c("Start_date", "Ki", "Ki_red", "NLL")
  # ems_output$Start_date <- as.Date(ems_output$Start_date, origin = '2020-01-01')
  ems_output$Start_date <- "" # as.Date(sim_ems$startdate, format="yyyy-mm-")


  # loop over simulation scenarios and record likelihood
  
  for (j in 1:length(scens)) {
    # pull out all simulation values of given Ki value
    sim_ems_subset <- sim_ems[which(sim_ems$scen_num == scens[j]), ]
    # Set the start date to be that based on when we started disease interventions
    # sim_ems_subset$time <- as.Date(sim_ems_subset$time,origin = (as.Date("2020-03-12") - floor(sim_ems_subset$socialDistance_time1[1])))
    sim_ems_subset$time <- as.Date(sim_ems_subset$startdate)

    # Get earliest and latest dates of the simualtion data and hopital date
    mindate <- max(min(sim_ems_subset$time), min(hosp_data_ems$date_of_extract))
    maxdate <- min(max(sim_ems_subset$time), max(hosp_data_ems$date_of_extract))

    # get rid of dates that don't overlap for comparison'
    sim_ems_subset1 <- sim_ems_subset # sim_ems_subset[which(sim_ems_subset$time >= mindate & sim_ems_subset$time <= maxdate),]
    hosp_data_ems_subset <- hosp_data_ems # hosp_data_ems[which(hosp_data_ems$date_of_extract >= mindate & hosp_data_ems$date_of_extract <= maxdate),]

    # Repeat process for simulation data and hosp admission data
    mindate <- max(min(sim_ems_subset$time), min(pre_hosp_adm_data_ems$date))
    maxdate <- min(max(sim_ems_subset$time), max(pre_hosp_adm_data_ems$date))

    sim_ems_subset2 <- sim_ems_subset # sim_ems_subset[which(sim_ems_subset$time >= mindate & sim_ems_subset$time <= maxdate),]
    pre_hosp_adm_data_ems_subset <- pre_hosp_adm_data_ems # pre_hosp_adm_data_ems[which(pre_hosp_adm_data_ems$date >= mindate & pre_hosp_adm_data_ems$date <= maxdate),]

    # Repeat process for simulation data and hosp death data
    mindate <- max(min(sim_ems_subset$time), min(pre_hosp_det_data_ems$date))
    maxdate <- min(max(sim_ems_subset$time), max(pre_hosp_det_data_ems$date))

    sim_ems_subset3 <- sim_ems_subset # sim_ems_subset[which(sim_ems_subset$time >= mindate & sim_ems_subset$time <= maxdate),]
    pre_hosp_det_data_ems_subset <- pre_hosp_det_data_ems # pre_hosp_det_data_ems[which(pre_hosp_det_data_ems$date >= mindate & pre_hosp_det_data_ems$date <= maxdate),]


    # Calculate likelyhood
    # Likelyhood of simulation generating detected critical
    nll1 <- -1 * sum(dpois(hosp_data_ems_subset$confirmed_covid_icu, sim_ems_subset1$crit_det + 1e-10, log = TRUE))
    # Likelyhood of simulation generating detected covid deaths
    nll2 <- -1 * sum(dpois(hosp_data_ems_subset$confirmed_covid_deaths_prev_24h, sim_ems_subset1$death_det_24hr + 1e-10, log = TRUE))
    # Likelyhood of simulations generating admission data
    nll3 <- -1 * sum(dpois(pre_hosp_adm_data_ems_subset$cases, sim_ems_subset2$hosp_24hr + 1e-10, log = TRUE))
    # Likelyhood of simulations creating death data that doesn't come from EMresource.
    nll4 <- -1 * sum(dpois(pre_hosp_det_data_ems_subset$cases, sim_ems_subset$death_det_24hr + 1e-10, log = TRUE))
    # Summ all likelyhood, weighting nll1 and nll2 higher
    nll <- nll1 + nll2 + (nll3 + nll4) * (length(hosp_data_ems$confirmed_covid_icu) / length(pre_hosp_adm_data_ems$cases)) / 2

    # Put likelihood values and corresponding start date and Ki in output dataframe
    ems_output$Start_date[j] <- as.character(unique(sim_ems_subset$startdate)) # as.Date((as.Date("2020-03-12") - floor(sim_ems_subset$socialDistance_time1[1])))
    ems_output$Ki[j] <- sim_ems_subset$Ki[1]
    ems_output$Ki_red[j] <- sim_ems_subset$social_multiplier_4[1]
    ems_output$NLL[j] <- nll

  }

  # Create sheet of the 5% most likely parameter combinations
  nam <- paste("ems", i, "_use_values", sep = "")
  assign(nam, ems_output[which(ems_output$NLL < quantile(ems_output$NLL, prob = 1 - 95 / 100)), ])

  ems_output <- ems_output[which(ems_output$NLL < quantile(ems_output$NLL, prob = 1 - 95 / 100)), ]
  ems_output$ems <- i
  use_values_list[[i]] <- ems_output
}


## Set working directory to whereever you want results saved.
# Create figures showing correlations between paramter combinations for
# Each EMS region

library(cowplot)
f_paramplots <- function(use_values_dat, ems) {
  # use_values_dat=ems1_use_values

  best_param <- use_values_dat[which(use_values_dat$NLL == min(use_values_dat$NLL)), ]


  Ki_startdate <- ggplot(use_values_dat, aes(x = Start_date, y = Ki)) +
    geom_point() +
    labs(fill = "NLL") +
    ylim(0, 1) +
    labs(title = "Ki_red_startdate", subtitle = ems) +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)
    )

  Ki_red_startdate <- ggplot(use_values_dat, aes(x = Start_date, y = Ki_red)) +
    geom_point() +
    labs(fill = "NLL") +
    labs(title = "Ki_red_startdate", subtitle = ems) +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)
    )

  Ki_Ki_red <- ggplot(use_values_dat, aes(x = Ki, y = Ki_red)) +
    geom_point() +
    labs(fill = "NLL") +
    xlim(0, 1) +
    labs(title = "Ki_Ki_red", subtitle = ems, x = "\n\n\nKi")

  pplot <- plot_grid(Ki_startdate, Ki_red_startdate, Ki_Ki_red, nrow = 1)
  ggsave(paste0(ems, "_best_parameter_plots.png"),
    plot = pplot,
    path = file.path(out_dir,"best_parameter_plots/"), width = 13, height = 6, device = "png"
  )

  return(pplot)
}


### Generate plots with points for parameter ranges
for (i in c(1:11)) {
  ems_i <- paste0("EMS_", i)
  nam <- use_values_list[[i]]
  
  f_paramplots(use_values_dat = nam, ems = ems_i)

  # Save best paramter combinations
  write.csv(nam, paste0(out_dir,"best_parameter_sheets/best_parameter_ranges_ems", i, ".csv"))
}


### Export best parameter fit as csv for all EMS 
df_best <- do.call(rbind.data.frame, use_values_list) %>%
  group_by(ems) %>%
  filter(NLL == min(NLL)) %>%
  write.csv(file.path(out_dir,"best_parameters_emsAll2.csv"))


