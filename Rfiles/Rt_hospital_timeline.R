## ======================================================================================================
# R script that combined Rt estimates and trajectoriesDat to plot Rt against increase in hospitalizations
## ======================================================================================================


### Define functions and settings
customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 12, face = "bold"),
  strip.text.y = element_text(size = 12, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 18, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 18),
  plot.caption = element_text(size = 8),
  legend.title = element_text(size = 18),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)


## Helper function called in f_load_and_combine_dat
f_load_Rt <- function(exp_dir = exp_dir, fname) {
  if (sum(grep("csv", fname)) == 1) df <- read.csv(file.path(exp_dir, "estimatedRt", fname))
  if (sum(grep("Rdata", fname)) == 1) {
    load(file.path(exp_dir, "estimatedRt", fname))
    df <- Rt_dat
  }

  colnames(df) <- gsub("[(R]", "", colnames(df))
  colnames(df) <- gsub("[)]", "", colnames(df))
  df <- df %>% mutate(meanRtLE1 = ifelse(Median < 1, 1, 0))

  ### Adjust for biweely interval
  df <- df %>% mutate(t_start = t_start + 13, t_end = t_end + 13)

  return(df)
}


f_load_trajectories <- function(df = NULL, grepCol = "All", fname = "trajectoriesDat.csv") {
  
  if (is.null(df)) df <- read.csv(file.path(exp_dir, fname))


  outVars <- colnames(df)[grep(grepCol, colnames(df))]
  KiVars <- paste0("Ki_t_EMS_", c(1:11))
  groupvars <- c("startdate", "time", "scen_num", "reopening_multiplier_4")
  keepvars <- c(groupvars, outVars, KiVars)

  df <- df %>%
    dplyr::select(keepvars) %>%
    mutate(
      startdate = as.Date(startdate),
      Date = as.Date(time + startdate)
    ) %>%
    dplyr::mutate(Date <- as.character(Date))

  colnames(df) <- gsub(paste0("_", grepCol), "", colnames(df))

  df <- df %>%
    dplyr::group_by(scen_num, reopening_multiplier_4) %>%
    dplyr::arrange(Date) %>%
    mutate(
      new_hospitalized = hosp_cumul - lag(hosp_cumul),
      new_critical = crit_cumul - lag(crit_cumul),
      new_infected = infected_cumul - lag(infected_cumul)
    )

  df$time <- round(df$time, 0)
  df$region = grepCol

  ### TO DO for southern
  df$Ki <- (
    df$Ki_t_EMS_1 +
      df$Ki_t_EMS_2 +
      df$Ki_t_EMS_3 +
      df$Ki_t_EMS_4 +
      df$Ki_t_EMS_5 +
      df$Ki_t_EMS_6 +
      df$Ki_t_EMS_7 +
      df$Ki_t_EMS_8 +
      df$Ki_t_EMS_9 +
      df$Ki_t_EMS_10 +
      df$Ki_t_EMS_11) / 11

  if (region == "southern") {
    df$Ki <- (df$Ki_t_EMS_4 + df$Ki_t_EMS_5) / 2
  }
  if (region == "northeast") {
    df$Ki <- (df$Ki_t_EMS_7 +
                df$Ki_t_EMS_8 +
                df$Ki_t_EMS_9 +
                df$Ki_t_EMS_10 +
                df$Ki_t_EMS_11) / 5
  }
  if (region == "central") {
    df$Ki <- (df$Ki_t_EMS_3 + df$Ki_t_EMS_6) / 2
  }
  if (region == "northcentral") {
    df$Ki <- (df$Ki_t_EMS_1 + df$Ki_t_EMS_2) / 2
  }


  return(df)
}


f_combine_dat <- function(df_Rt, df_trajectories, region) {
  df_Rt <- df_Rt %>%
    merge(unique(df_trajectories[, c("time", "Date", "scen_num")]),
      by.x = c("t_start", "scen_num"), by.y = c("time", "scen_num")
    )

  if (tolower(region) %in% c("northcentral", "northeast", "central", "southern", "illinois", "all")) {
    regionsList <- list(
      "northcentral" = c(1, 2),
      "northeast" = c(7, 8, 9, 10, 11),
      "central" = c(3, 6),
      "southern" = c(4, 5),
      "illinois" = c(1:11)
    )

    ems <- as.numeric(regionsList[[region]])
    df_Rt <- df_Rt %>%
      filter(region %in% ems) %>%
      dplyr::group_by(Date, t_start, scen_num) %>%
      dplyr::summarize(
        Rt_mean = mean(Mean),
        Rt_median = mean(Median),
        Rt_std = mean(Std),
        Rt_q0.025 = mean(Quantile.0.025),
        Rt_q0.05 = mean(Quantile.0.05),
        Rt_q0.25 = mean(Quantile.0.25),
        Rt_q0.75 = mean(Quantile.0.75),
        Rt_q0.95 = mean(Quantile.0.95),
        Rt_q0.975 = mean(Quantile.0.975)
      )
  } else {
    df_Rt <- df_Rt %>%
      dplyr::rename(
        Rt_mean = Mean,
        Rt_median = Median,
        Rt_std = Std,
        Rt_q0.025 = Quantile.0.025,
        Rt_q0.05 = Quantile.0.05,
        Rt_q0.25 = Quantile.0.25,
        Rt_q0.75 = Quantile.0.75,
        Rt_q0.95 = Quantile.0.95,
        Rt_q0.975 = Quantile.0.975
      )
  }


  mergevars <- colnames(df_trajectories)[colnames(df_trajectories) %in% colnames(df_Rt)]
  df_Rt <- as.data.frame(df_Rt)
  df_trajectories <- as.data.frame(df_trajectories)
  df_trajectories$Date <- as.character(df_trajectories$Date)
  df_Rt$Date <- as.character(df_Rt$Date)


  dat_combined <- df_trajectories %>%
    merge(df_Rt, by = mergevars) %>%
    mutate(
      Date = as.Date(Date),
      reopening = round(reopening_multiplier_4, 2)
    )

  return(dat_combined)
}


## Helper function called in f_stacked_timelines
f_timelinePlot <- function(df, channel, startdate, enddate) {
  df <- as.data.frame(df)
  df$Date <- as.Date(df$Date)
  df <- subset(df, Date >= as.Date(startdate) & Date <= as.Date(enddate))

  
  library(RColorBrewer)
  nb.cols <- length(unique(df$reopening))
  customcols <- colorRampPalette(brewer.pal(8, "Dark2"))(nb.cols)
  
  df$channel <- df[, colnames(df) == channel]
  pplot <- df %>%
    ggplot() +
    geom_line(aes(x = Date, y = channel, col = as.factor(reopening * 100)), size = 1.3) +
    labs(
      y = "",
      x = "",
      col = "Reopening (%)"
    ) +
    scale_x_date(date_breaks = "2 week", date_labels = "%d%b", lim = c(as.Date(startdate), as.Date(enddate)))+
    scale_color_manual(values = customcols) 

  return(pplot)
}


f_stacked_timelines <- function(df_combined = dat_combined, startdate, enddate,
                                startReopen = "2020-06-21", endReopen = "2020-07-27", SAVE = TRUE) {
  p0 <- df_combined %>%
    dplyr::group_by(Date, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(Ki = mean(Ki)) %>%
    f_timelinePlot(channel = "Ki", startdate, enddate) +
    geom_vline(xintercept = c(as.Date(startReopen), as.Date(endReopen))) +
    labs(title = "Ki") +
    theme(legend.position = "none")


  p1 <- df_combined %>%
    dplyr::group_by(Date, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(Rt_mean = mean(Rt_mean)) %>%
    mutate(Date = Date ) %>%
    f_timelinePlot(channel = "Rt_mean", startdate, enddate) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    geom_vline(xintercept = c(as.Date(startReopen), as.Date(endReopen))) +
    labs(title = "Rt") +
    theme(legend.position = "none")

  p2 <- df_combined %>%
    dplyr::group_by(Date, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(new_infected = mean(new_infected)) %>%
    f_timelinePlot(channel = "new_infected", startdate, enddate) +
    geom_vline(xintercept = c(as.Date(startReopen), as.Date(endReopen))) +
    labs(title = "new_infected") +
    theme(legend.position = "none")


  p3 <- df_combined %>%
    dplyr::group_by(Date, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(new_hospitalized = mean(new_hospitalized)) %>%
    f_timelinePlot(channel = "new_hospitalized", startdate, enddate) +
    geom_vline(xintercept = c(as.Date(startReopen), as.Date(endReopen))) +
    labs(title = "new_hospitalized")

  legend <- get_legend(p3)
  p3 <- p3 + theme(legend.position = "none")

  pall <- plot_grid(p0, p1, p2, p3, ncol = 1)
  pall <- plot_grid(pall, legend, ncol = 2, rel_widths = c(2,0.5), rel_heights = c(1,0.5))


  if (SAVE) {
    ggsave(paste0("reopening_timelines_", region, ".pdf"),
      plot = pall, path = file.path(exp_dir), width = 8, height = 12, device = "pdf"
    )
    ggsave(paste0("reopening_timelines_", region, "png"),
      plot = pall, path = file.path(exp_dir), width = 8, height = 12, device = "png"
    )
  }
  return(pall)
}


#### Calculate weekly increase and plot against Rt
f_Rt_hosp_scatter_plot <- function(df_combined, startdate, enddate, SAVE=TRUE) {
  library(lubridate)
  timetitle <- paste0("Time: ", startdate, " to ", enddate)

  weeklyHosp <- df_combined %>%
    dplyr::mutate(week = week(Date)) %>%
    dplyr::group_by(week, scen_num, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(new_hospitalized_weekavrg = mean(new_hospitalized, na.rm = TRUE)) %>%
    dplyr::group_by(scen_num, reopening_multiplier_4, reopening) %>%
    arrange(week) %>%
    dplyr::mutate(new_hospitalized_weekavrg_perc = (new_hospitalized_weekavrg - lag(new_hospitalized_weekavrg)) / lag(new_hospitalized_weekavrg))

  pdat0 <- df_combined %>%
    dplyr::mutate(week = week(Date)) %>%
    left_join(weeklyHosp, by = c("week", "scen_num", "reopening_multiplier_4", "reopening")) %>%
    mutate(Date = Date) %>%
    dplyr::group_by(week, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(Rt_mean = mean(Rt_mean))


  p0 <- df_combined %>%
    mutate(week = week(Date)) %>%
    left_join(weeklyHosp, by = c("week", "scen_num", "reopening_multiplier_4", "reopening")) %>%
    mutate(Date = Date ) %>%
    dplyr::group_by(Date, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(Rt_mean = mean(Rt_mean)) %>%
    f_timelinePlot(channel = "Rt_mean", startdate, enddate) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    geom_hline(yintercept = -Inf) +
    geom_vline(xintercept = -Inf) +
    customThemeNoFacet


  p1 <- df_combined %>%
    dplyr::filter(Date >= as.Date("2020-06-21")) %>%
    mutate(week = week(Date)) %>%
    left_join(weeklyHosp, by = c("week", "scen_num", "reopening_multiplier_4", "reopening")) %>%
    dplyr::filter(Date >= as.Date(startdate) & Date <= as.Date(enddate)) %>%
    dplyr::group_by(Date, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(new_hospitalized_weekavrg_perc = mean(new_hospitalized_weekavrg_perc * 100)) %>%
    f_timelinePlot(channel = "new_hospitalized_weekavrg_perc", startdate, enddate)  +
    geom_hline(yintercept = -Inf) +
    geom_vline(xintercept = -Inf) +
    customThemeNoFacet


  p3 <- df_combined %>%
    mutate(week = week(Date)) %>%
    left_join(weeklyHosp, by = c("week", "scen_num", "reopening_multiplier_4", "reopening")) %>%
    filter(Date >= as.Date(startdate) & Date <= as.Date(enddate)) %>%
    filter(new_hospitalized_weekavrg_perc >= -0.5 & new_hospitalized_weekavrg_perc < 0.8) %>%
    dplyr::group_by(Date, week, reopening_multiplier_4, reopening) %>%
    dplyr::summarize(new_hospitalized_weekavrg_perc = mean(new_hospitalized_weekavrg_perc)) %>%
    left_join(pdat0, by = c("week", "reopening_multiplier_4", "reopening")) %>%
    ggplot() +
    geom_smooth(aes(x = new_hospitalized_weekavrg_perc, y = Rt_mean)) +
    geom_point(aes(x = new_hospitalized_weekavrg_perc, y = Rt_mean, group = as.factor(reopening))) +
    labs(x = "\nWeekly increase in new hospitalizations (%)", y = "\nEstimated Rt", subtitle = timetitle) +
    scale_x_continuous(breaks = seq(-0.2, 0.6, 0.1), labels = seq(-0.2, 0.6, 0.1) * 100, limits = c(-0.2,0.6)) +
    scale_y_continuous(breaks = seq(0.8, 1.5, 0.1), labels = seq(0.8, 1.5, 0.1)) +
    geom_hline(yintercept = 1, linetype = "dashed") +
    geom_hline(yintercept = -Inf) +
    geom_vline(xintercept = -Inf) +
    customThemeNoFacet


  p0 <- p0 + theme(legend.position = "none") + labs(subtitle = "Estimated Rt")
  p1 <- p1 + theme(legend.position = "none") + labs(subtitle = "Weekly increase in new hospitalizations (%)")
  p10 <- plot_grid(p0, p1, nrow = 1, rel_widths = c(1, 1))
  pplot <- plot_grid(p10, p3, ncol = 1, rel_heights = c(0.5, 1))
  pplot <- plot_grid(pplot, NULL, ncol = 2, rel_widths = c(1, 0.1))
  

  if (SAVE) {
    ggsave(paste0("Rt_vs_newhospitalizations_", region, ".pdf"),
      plot = pplot, path = file.path(exp_dir), width = 12, height = 8, device = "pdf"
    )

    ggsave(paste0("Rt_vs_newhospitalizations_", region, ".png"),
      plot = pplot, path = file.path(exp_dir), width = 12, height = 8, device = "png"
    )
  }


  return(pplot)
}



#### ===================================
## Run script
#### ===================================
packages_needed <- c("tidyverse", "scales")
lapply(packages_needed, require, character.only = TRUE)

theme_set(theme_minimal())

## Load directories and custom objects and functions
Location="LOCAL"
if(Location=="NUCLUSTER"){
  setwd("/projects/p30781/covidproject/covid-chicago/Rfiles/")
}
source("load_paths.R")

exp_name <- "20200803_IL_baseline_reopeningScenarios"
exp_dir <- file.path(simulation_output, exp_name)

### Get trajectories
region <- "All" #
grepCol <- region
if (region == "All" | region == "IL") grepCol <- "All"

startdate <- "2020-06-15"
enddate <- "2020-08-21"


### If file size is large, load only once and then set to FALSE
loadDat=FALSE
if(loadDat)trajectoriesDat <- read.csv(file.path(exp_dir, "trajectoriesDat.csv"))

Rtdat <- f_load_Rt(exp_dir, fname = "combined_temp_Rt_tempdat_All.Rdata") %>% as.data.frame()
dat <- f_load_trajectories(df = trajectoriesDat, grepCol = grepCol, fname = "trajectoriesDat.csv") %>% as.data.frame()

## Combine Rt and trajectories
dat_combined <- f_combine_dat(df_Rt=Rtdat, df_trajectories=dat, region=region)

f_stacked_timelines(df_combined = dat_combined, startdate, enddate, SAVE=TRUE)

f_Rt_hosp_scatter_plot(df_combined = dat_combined, startdate, enddate, SAVE=TRUE)



