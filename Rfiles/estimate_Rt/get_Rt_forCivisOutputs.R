## ============================================================
## R script to get R(t) from simulation outputs
## ============================================================

# install.packages("devtools")
# library(devtools)
# install_github("annecori/EpiEstim", force = TRUE)
library(tidyverse)
library(data.table)
library(cowplot)
library(EpiEstim)


runInBatchMode <- TRUE

if (runInBatchMode) {
  cmd_agrs <- commandArgs()
  length(cmd_agrs)
  exp_name <- cmd_agrs[length(cmd_agrs) - 2]
  Location <- cmd_agrs[length(cmd_agrs) - 1]
  workingDir <- cmd_agrs[length(cmd_agrs)]
} else {
  exp_name <- "20200911_IL_test_v3"
  Location <- "Local"
  workingDir <- getwd()
}

print(workingDir)
source(file.path(workingDir,"load_paths.R"))
source("processing_helpers.R")
source("estimate_Rt/getRt_function.R")

#### Experiment settings
expsplit <- strsplit(exp_name, "_")[[1]]
simdate <- expsplit[1]
exp_scenario <- expsplit[length(expsplit)]
fname <- paste0("nu_", simdate, ".csv")
exp_dir <- file.path(simulation_output, exp_name)

run_Rt_estimation <- function(dat = dat, method = "uncertain_si", weekwindow = 13) {
  Rt_list <- list()
  si_list <- list()
  
  for (region in unique(dat$geography_modeled)) {
    # region = unique(dat$geography_modeled)[1]
    disease_incidence_data <- dat %>%
      filter(geography_modeled == region) %>%
      rename(I = cases_new_median)
    
    
    res <- getRt(disease_incidence_data, method = method, weekwindow = weekwindow)
    
    
    pplot <- plot(res)
    ggsave(paste0(region, "_EpiEstim_default_", method, ".pdf"),
           plot = pplot, path = file.path(exp_dir, "_plots"), width = 6, height = 10, dpi = 300, device = "pdf"
    )
    
    Rt_list[[region]] <- res$R %>% mutate(region = region, weekwindow = weekwindow)
    si_list[[region]] <- res$SI.Moments %>% mutate(region = region, weekwindow = weekwindow)
  }
  
  ### Combine list to dataframe
  Rt_dat <- Rt_list %>%
    bind_rows() %>%
    dplyr::mutate(time = t_end) %>%
    dplyr::rename(geography_modeled = region) %>%
    dplyr::rename(
      rt_median = `Median(R)`,
      rt_lower = `Quantile.0.025(R)`,
      rt_upper = `Quantile.0.975(R)`
    ) %>%
    mutate(date = as.Date("2020-02-13") + time)
  
  
  RtdatCombined <- dat %>%
    dplyr::mutate(date = as.Date(date)) %>%
    arrange(geography_modeled, date) %>%
    dplyr::group_by(geography_modeled) %>%
    # mutate(time = c(1:n_distinct(date))) %>%
    merge(Rt_dat, by = c("geography_modeled", "date"), all.x = TRUE) %>%
    dplyr::filter(geography_modeled %in% c("illinois", paste0("covidregion_", c(1:11)))) %>%
    dplyr::select(
      date, geography_modeled, scenario_name, cases_median, cases_lower, cases_upper, cases_new_median, cases_new_lower, cases_new_upper,
      deaths_median, deaths_lower, deaths_upper, deaths_det_median, deaths_det_lower, deaths_det_upper, hosp_bed_median, hosp_bed_lower, hosp_bed_upper,
      icu_median, icu_lower, icu_upper,
      vent_median, vent_lower, vent_upper, recovered_median, recovered_lower, recovered_upper, rt_median, rt_lower, rt_upper
    )
  
  
  ### Save combined dataframe
  if (dim(dat)[1] == dim(RtdatCombined)[1]) {
    fwrite(RtdatCombined, file = file.path(exp_dir, fname), row.names = FALSE, quote = FALSE)
    
    ### Export subset region 10 and 11 for cdph
    ### Keep only Rt channels 
    regionsubset <- c("covidregion_10","covidregion_11")
    RtdatCombined %>% 
      dplyr::filter(geography_modeled %in% regionsubset) %>%
      dplyr::filter(date  <= as.Date(Sys.Date())) %>%
      dplyr::select(date, geography_modeled, scenario_name,rt_median, rt_lower, rt_upper) %>%
      fwrite(file = file.path(exp_dir, gsub("nu_","nu_cdph_Rt_",fname)), row.names = FALSE, quote = FALSE)
  }
  
  return(RtdatCombined)
}


#### Run code
dat <- fread(file.path(exp_dir, fname))


### Rt estimation
if (!("rt_median" %in% colnames(dat))) {
  RtdatCombined = run_Rt_estimation(dat = dat, method = "uncertain_si", weekwindow = 13)
} else {
  ## For plotting
  RtdatCombined <- dat %>%  mutate( region = gsub("covidregion_", "", geography_modeled), date= as.Date(date))
}

### Plots
generatePlots <- TRUE
if (generatePlots) {
  
  RtdatCombined$region <- factor(RtdatCombined$geography_modeled, levels = paste0("covidregion_", c(1:11)), labels = c(1:11))

  pplot <- RtdatCombined %>%
    filter(date >= "2020-04-01") %>%
    filter(region %in% as.character(c(1:11))) %>%
    ggplot() +
    theme_cowplot() +
    geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue3", alpha = 0.3) +
    geom_line(aes(x = date, y = rt_median), col = "deepskyblue3") +
    facet_wrap(~region, scales = "free_x") +
    theme(panel.spacing = unit(1, "lines")) +
    geom_hline(yintercept = 1) +
    geom_hline(yintercept = c(-Inf, Inf)) +
    geom_vline(xintercept = c(-Inf, Inf)) +
    customThemeNoFacet +
    labs(y = expression(italic(R[t])), caption = "Shaded area = uncertainity in Rt estimation") +
    scale_x_date(date_breaks = "30 days", date_labels = "%d\n%b")

  ggsave(paste0("estimatedRt_overtime.png"),
    plot = pplot, path = file.path(exp_dir, "_plots"), width = 12, height = 8, device = "png"
  )
  ggsave(paste0("estimatedRt_overtime.pdf"),
    plot = pplot, path = file.path(exp_dir, "_plots"), width = 12, height = 8, device = "pdf"
  )

  rm(pplot)


  pplot <- RtdatCombined %>%
    filter(date >= "2020-04-01") %>%
    filter(geography_modeled == "illinois") %>%
    ggplot() +
    theme_cowplot() +
    geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue3", alpha = 0.3) +
    geom_line(aes(x = date, y = rt_median), col = "deepskyblue3") +
    geom_hline(yintercept = 1) +
    geom_hline(yintercept = c(-Inf, Inf)) +
    geom_vline(xintercept = c(-Inf, Inf)) +
    customThemeNoFacet +
    labs(y = expression(italic(R[t])), caption = "Shaded area = uncertainity in Rt estimation") +
    scale_x_date(date_breaks = "30 days", date_labels = "%d\n%b")

  ggsave(paste0("IL_estimatedRt_overtime.png"),
    plot = pplot, path = file.path(exp_dir, "_plots"), width = 8, height = 6, device = "png"
  )
  ggsave(paste0("IL_estimatedRt_overtime.pdf"),
    plot = pplot, path = file.path(exp_dir, "_plots"), width = 8, height = 6, device = "pdf"
  )

  rm(pplot)


  ### Change date to today
  pplot <- RtdatCombined %>%
    filter(date >= as.Date(simdate, format = "%Y%m%d") & date < as.Date(simdate, format = "%Y%m%d") + 1) %>%
    filter(region %in% as.character(c(1:11))) %>%
    ggplot() +
    theme_cowplot() +
    geom_errorbar(aes(x = reorder(region, rt_median), ymin = rt_lower, ymax = rt_upper), width = 0.3, alpha = 0.3) +
    geom_point(aes(x = reorder(region, rt_median), y = rt_median), col = "deepskyblue3", size = 2.5) +
    geom_hline(yintercept = 1) +
    labs(
      y = expression(italic(R[t])),
      x = "Covid region ordered by median Rt",
      subtitle = paste0("\n Estimated Rt for ", as.Date(simdate, format = "%Y%m%d")),
      caption = "Error bounds based on uncertainty in Rt estimation"
    ) +
    customThemeNoFacet


  ### Change name suffix to today
  ggsave(paste0("estimatedRt_today.png"),
    plot = pplot, path = file.path(exp_dir, "_plots"), width = 8, height = 5, device = "png"
  )


  ##### Overlaid with hospital overflow
  nu_hospitaloverflow <- fread(file.path(simulation_output, exp_name, paste0("nu_hospitaloverflow_", simdate, ".csv")))
  dt <- nu_hospitaloverflow %>% mutate(date_window_upper_bound = as.Date(date_window_upper_bound), region = gsub("covidregion_", "", geography_modeled))

  dt$region <- factor(dt$region, levels = c(1:11), labels = c(1:11))
  RtdatCombined$region <- factor(RtdatCombined$region, levels = c(1:11), labels = c(1:11))
  RtdatCombined$date <- as.Date(RtdatCombined$date)


  plot_end_date <- unique(max(dt$date_window_upper_bound, na.rm = TRUE))
  plot_start_date <- as.Date(simdate, format = "%Y%m%d") - 60

  pplot <- RtdatCombined %>%
    filter(date >= plot_start_date & date <= plot_end_date) %>%
    filter(region %in% as.character(c(1:11))) %>%
    ggplot() +
    theme_cowplot() +
    geom_rect(xmin = -Inf, xmax = as.Date(simdate, format = "%Y%m%d"), ymin = -Inf, ymax = Inf, fill = "lightgrey", alpha = 0.02) +
    geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue3", alpha = 0.4) +
    geom_line(aes(x = date, y = rt_median), col = "deepskyblue3") +
    geom_hline(yintercept = 1) +
    geom_line(
      data = subset(dt),
      aes(
        x = date_window_upper_bound, y = percent_of_simulations_that_exceed + 1,
        col = as.factor(overflow_threshold_percent), linetype = resource_type,
        group = interaction(resource_type, overflow_threshold_percent)
      ), size = 1
    ) +
    facet_wrap(~region, nrow = 3) +
    scale_y_continuous(expr(italic(R[t])), sec.axis = sec_axis(~ . - 1, name = " overflow\nprobability")) +
    labs(x = "", color = "overflow threshold (%)", linetype = "resource type") +
    geom_hline(yintercept = c(-Inf, Inf)) +
    geom_vline(xintercept = c(-Inf, Inf)) +
    scale_color_manual(values = c("lightcoral", "firebrick4")) +
    customThemeNoFacet

  ggsave(paste0("estimatedRt_overtime_withOverflow.png"),
    plot = pplot, path = file.path(exp_dir, "_plots"), width = 12, height = 6, device = "png"
  )
}
