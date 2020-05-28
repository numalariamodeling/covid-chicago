## ==================================================
# R script that analysis trajectoriesDat
## ==================================================

require(tidyverse)
require(cowplot)
require(scales)
require(lattice)
require(readxl)
require(viridis)

gitdir <- file.path("C:/Users/mrung/gitrepos/covid-chicago")
datadir <- file.path("C:/Users/mrung/Box/NU-malaria-team/data")
projectdir <- file.path("C:/Users/mrung/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/contact_tracing/")

source(file.path(gitdir, "Rfiles/f_AggrDat.R"))
source(file.path(gitdir, "Rfiles/setup.R"))


load_capacity <- function(selected_ems) {
  ems_df <- read_excel(file.path(datadir, "covid_IDPH/Corona virus reports/EMS_report_2020_03_21.xlsx"))
  ems_df <- ems_df %>%
    filter(Date == as.Date("2020-03-27")) %>%
    separate(Region, into = c("ems", "Hospital"), sep = "-") %>%
    mutate(
      hospitalized = `Total_Med/_Surg_Beds`,
      critical = `Total_Adult_ICU_Beds`,
      ventilators = `Total_Vents`
    )

  capacity <- ems_df %>%
    filter(ems == selected_ems) %>%
    dplyr::select(hospitalized, critical, ventilators)

  return(capacity)
}

# exp_name ="20200414_NMH_catchment_testInterventionStop_rn50"
simdate <- "20200528"
exp_name <- "20200528_IL_EMSgrp_heatmap"

reopeningdate <- as.Date("2020-06-01")
evaluation_window <- c(reopeningdate, reopeningdate + 60)

trajectoriesDat <- read.csv(file.path(projectdir, simdate, exp_name, "/trajectoriesDat.csv"), header = TRUE)
trajectoriesDat <- subset(trajectoriesDat, time >= 100 & time <= 300)


## load predictions
getdata <- function(ems) {
  # emsvars <- colnames(trajectoriesDat)[grep("[.]",colnames(trajectoriesDat))]
  emsvars <- c(
    "susceptible_EMS.", "exposed_EMS.", "asymptomatic_EMS.", "symptomatic_mild_EMS.", "symptomatic_severe_EMS.",
    "hospitalized_EMS.", "critical_EMS.", "deaths_EMS.", "recovered_EMS.", "asymp_cumul_EMS.",
    "asymp_det_cumul_EMS.", "symp_mild_cumul_EMS.", "symp_severe_cumul_EMS.", "hosp_cumul_EMS.", "hosp_det_cumul_EMS.",
    "crit_cumul_EMS.", "crit_det_cumul_EMS.", "crit_det_EMS.", "death_det_cumul_EMS.", "infected_EMS.",
    "infected_cumul_EMS.", "symp_mild_det_cumul_EMS.", "symp_severe_det_cumul_EMS.", "detected_EMS.", "detected_cumul_EMS.",
    "presymptomatic_EMS."
  )

  emsvars <- paste0(emsvars, ems)

  groupvars <- c("time", "startdate", "scen_num", "sample_num", "run_num", "time_to_detection", "d_As_ct1", "reduced_inf_of_det_cases")
  (keepvars <- c(groupvars, emsvars))

  subdat <- trajectoriesDat %>% dplyr::select(keepvars)

  subdat <- subdat %>%
    pivot_longer(cols = -c(groupvars)) %>%
    mutate(
      startdate = as.Date(startdate),
      Date = as.Date(time + startdate),
      isolation_success = 1 - reduced_inf_of_det_cases,
      name = gsub("All", "EMS.IL", name)
    ) %>%
    separate(name, into = c("outcome", "region"), sep = "_EMS[.]")
  head(subdat)


  unique(subdat$time_to_detection)
  unique(subdat$reduced_inf_of_det_cases)
  unique(subdat$d_As_ct1)
  unique(subdat$startdate)

  ### group column names
  cumul_channels <- unique(grep("cumul", colnames(subdat), value = TRUE))


  ### what time point to select?
  tempdat <- subdat %>%
    filter(Date >= evaluation_window[1] & Date <= evaluation_window[2] + 30) %>%
    select(-c(time, sample_num, scen_num, run_num)) %>%
    group_by(Date, region, d_As_ct1, reduced_inf_of_det_cases, isolation_success, time_to_detection, outcome) %>%
    summarize(value.mean = mean(value)) %>%
    group_by() %>%
    mutate(
      d_As_ct1_fct = ifelse(d_As_ct1 < 0.5, "low", "high"),
      isolation_success_fct = ifelse(isolation_success < 0.5, "low", "high"),
      time_to_detection = round(time_to_detection, 1),
      d_As_ct1_label = ifelse(d_As_ct1_fct == "low", "low contact tracing &", "high contact tracing &"),
      isolation_success_label = ifelse(isolation_success_fct == "low", "low isolation success", " high isolation success")
    ) %>%
    dplyr::arrange(d_As_ct1, isolation_success, time_to_detection, outcome, Date) %>%
    dplyr::group_by(d_As_ct1, isolation_success, time_to_detection, outcome, region) %>%
    mutate(
      diff = value.mean - lag(value.mean),
      growthRate = (value.mean - lag(value.mean)) / lag(value.mean),
      mean_growthRate = mean(growthRate, na.rm = T)
    )
  return(tempdat)
}

f_heatmap <- function(df, selected_outcome, valuetype = "absolute") {
  if (selected_outcome == "ventilators") {
    dat <- df %>%
      filter(outcome == "crit_det") %>%
      mutate(value.mean = value.mean * 0.660) %>%
      as.data.frame()
  } else {
    dat <- df %>%
      filter(outcome == selected_outcome) %>%
      as.data.frame()
  }

  x <- dat$d_As_ct1
  y <- dat$isolation_success
  if (valuetype == "absolute") z <- dat$value.mean
  if (valuetype == "growth") z <- dat$growthRate

  xyzmodel <- lm(z ~ y + x)

  xnew <- seq(0, 1, 0.01)
  ynew <- seq(0, 1, 0.01)
  # ...calculating prediction
  matdat <- expand.grid(x = xnew, y = ynew)
  matdat$z <- predict(xyzmodel, newdata = matdat)

  ### Load capacityDat
  ems <- unique(df$region)
  capacity <- load_capacity(ems)
  capacity$deaths <- 0

  if (!selected_outcome %in% names(capacity)) threshold <- round(summary(matdat$z)["1st Qu."], 0)
  if (selected_outcome %in% names(capacity)) threshold <- round(as.numeric(capacity[selected_outcome]), 0)


  tdat <- matdat %>%
    filter(z <= threshold) %>%
    dplyr::group_by(x) %>%
    dplyr::summarize(ythreshold = min(y))
  matdat <- left_join(matdat, tdat, by = "x")

  # if(valuetype=="absolute")flabel =  paste0(selected_outcome, "\n absolute predictions")
  # if(valuetype=="growth")flabel =  paste0(selected_outcome, "\n mean growth rate (%)")
  if (valuetype == "absolute") flabel <- paste0("absolute predictions")
  if (valuetype == "growth") flabel <- paste0("mean growth rate (%)")


  # https://stackoverflow.com/questions/14290364/heatmap-with-values-ggplot2
  matdatp <- ggplot(matdat, aes(x, y)) +
    geom_tile(aes(fill = z)) +
    # geom_text(aes(label = exposed), size = 5) +
    geom_line(aes(x = x, y = ythreshold)) +
    # scale_fill_gradient(low = "white", high = "red") +
    scale_fill_viridis(option = "C", discrete = FALSE, direction = -1) +
    labs(
      title = selected_outcome,
      x = "detections (P, As, Sym) (%)",
      y = "isolation success (%)",
      fill = flabel,
      col = "", shape = "",
      linetype = "",
      caption = paste0("Threshold: ", threshold)
    ) +
    customTheme_noAngle +
    scale_x_continuous(breaks = seq(0, 1, 0.2), labels = seq(0, 1, 0.2) * 100, expand = c(0, 0)) +
    scale_y_continuous(breaks = seq(0, 1, 0.2), labels = seq(0, 1, 0.2) * 100, expand = c(0, 0))

  return(matdatp)
}


## Parameter combinations that did run
sink(file.path(projectdir, simdate, exp_name, "parameter_combinations.txt"))
  #\ntable(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
  table(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
  #\ntable(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
  table(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
sink()


for (ems in c(1:11)) {
  # ems <- 2
  ems_dir <- file.path(projectdir, simdate, exp_name, paste0("EMS_", ems))
  if (!dir.exists(ems_dir)) dir.create(ems_dir)

  capacity <- load_capacity(ems)
  capacity$deaths <- 0


  tempdat <- getdata(ems)
  write.csv(tempdat, file.path(ems_dir, paste0("EMS_", ems, "_dat.csv")))

  ### what time point to select?   - calculate mean over timeperiod ?
  ### Aggregate time for heatmap
  dfAggr <- tempdat %>%
    dplyr::select(-Date) %>%
    dplyr::group_by(region, d_As_ct1, isolation_success, time_to_detection, outcome) %>%
    dplyr::summarize_all(.funs = "mean", na.rm = T)


  for (selected_outcome in c("critical", "hospitalized", "deaths", "ventilators")) {
    
    capacityline <- as.numeric(capacity[colnames(capacity) == selected_outcome])
    
    if (selected_outcome == "ventilators") {
      plotdat <- tempdat %>%
        filter(outcome == "crit_det") %>%
        mutate(value.mean = value.mean * 0.660) %>%
        as.data.frame()

      threshold_param <- dfAggr %>%
        filter(outcome == "crit_det") %>%
        mutate(value.mean = value.mean * 0.660) %>%
        mutate(capacity = capacityline) %>%
        filter(
          value.mean <= capacity &
            d_As_ct1 == min(d_As_ct1) &
            isolation_success == min(isolation_success)
        ) %>%
        dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
    } else {
      plotdat <- tempdat %>%
        filter(outcome == selected_outcome) %>%
        as.data.frame()

      threshold_param <- dfAggr %>%
        mutate(capacity = capacityline) %>%
        filter(outcome == selected_outcome) %>%
        filter(
          value.mean <= capacity &
            d_As_ct1 == min(d_As_ct1) &
            isolation_success == min(isolation_success)
        ) %>%
        dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
    }

    write.csv(threshold_param, file.path(ems_dir, paste0("EMS_", ems,"_",selected_outcome, "_thresholds.csv")))



    l_plot <- ggplot(data = plotdat) + theme_cowplot() +
      # geom_vline(xintercept=as.Date("2020-08-02"), linetype="dashed")+
      geom_line(aes(x = Date, y = value.mean, group = interaction(isolation_success, d_As_ct1)), size = 1.3, col = "deepskyblue4") +
      facet_wrap(~time_to_detection) +
      labs(
        title = paste0("EMS ", unique(plotdat$region)),
        caption = "each lines represents an unique combinations of isolation success and detection rate",
        subtitle = "test delay (days)", y = selected_outcome
      )

    ggsave(paste0("EMS_", ems, "_", selected_outcome, "_line.png"),
      plot = l_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "png"
    )

    # selected_outcome = "critical"
    p_plot <- ggplot(data = subset(plotdat, Date >= as.Date("2020-08-01") & Date < as.Date("2020-08-03"))) + theme_cowplot() +
      geom_point(aes(x = d_As_ct1, y = value.mean, col = isolation_success, shape = as.factor(time_to_detection)), size = 2.3) +
      labs(
        title = paste0("EMS ", unique(tempdat$region)),
        subtitle = "1 months after reopening",
        shape = "test delay (days)",
        x = "detection rate (P, As, Sym)",
        y = selected_outcome
      ) +
      scale_color_viridis(option = "D", discrete = FALSE, direction = -1) +
      geom_hline(yintercept = capacityline, linetype = "dashed")

    ggsave(paste0("EMS_", ems, "_", selected_outcome, "_scatter.png"),
      plot = p_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "png"
    )


    for (testDelay in unique(dfAggr$time_to_detection)) {
      h_plot <- f_heatmap(subset(dfAggr, time_to_detection == testDelay), selected_outcome, valuetype = "absolute")
      ggsave(paste0("EMS_", ems, "_", selected_outcome, "_tD", testDelay, "_heatmap.png"),
        plot = h_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "png"
      )
      rm(h_plot)
    }
  }
}


#### Extract minium value per ems and per outcome and plot + csv summary table
