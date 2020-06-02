## ==================================================
# R script that analysis trajectoriesDat
## ==================================================

require(tidyverse)
require(cowplot)
require(scales)
require(lattice)
require(readxl)
require(viridis)
require(stringr)

source("load_paths.R")
source("processing_helpers.R")


ct_dir <- file.path(simulation_output, "contact_tracing")

# Define experiment iteration and simdate
simdate <- "20200601"

nexps <- list.files(file.path(ct_dir, simdate))
exp_name <- simdate
exp_dir <- file.path(ct_dir, simdate)


##--------------------------------------------
## Define functions 
##--------------------------------------------

reopeningdate <- as.Date("2020-06-01")
evaluation_window <- c(reopeningdate, reopeningdate + 60)


#getdata
getdata <- function(selected_ems) {
  #'  getdata is per default using the "trajectoriesDat" dataset to perfom specific data editing
  #'  Outcome variables of interest are selected for one or more EMS regions as specified in selected_ems
  #'  If multiple integers are included in the selected_ems, the data will be aggregated
  #'  The data is filtered by date to include only dates within the defined evaluation window
  #'  Factor variables per contact tracing parameter are generated to 
  #'  optionally facilitate plotting or custom tables for data exploration
  #' @param selected_ems  vector of integers representing one or multiple EMS areas

  
  # emsvars <- colnames(trajectoriesDat)[grep("[.]",colnames(trajectoriesDat))]
  emsvars_temp <- c(
    "susceptible_EMS.", "exposed_EMS.", "asymptomatic_EMS.", "symptomatic_mild_EMS.", "symptomatic_severe_EMS.",
    "hospitalized_EMS.", "critical_EMS.", "deaths_EMS.", "recovered_EMS.", "asymp_cumul_EMS.",
    "asymp_det_cumul_EMS.", "symp_mild_cumul_EMS.", "symp_severe_cumul_EMS.", "hosp_cumul_EMS.", "hosp_det_cumul_EMS.",
    "crit_cumul_EMS.", "crit_det_cumul_EMS.", "crit_det_EMS.", "death_det_cumul_EMS.", "infected_EMS.",
    "infected_cumul_EMS.", "symp_mild_det_cumul_EMS.", "symp_severe_det_cumul_EMS.", "detected_EMS.", "detected_cumul_EMS.",
    "presymptomatic_EMS."
  )

  emsvars <- NULL
  for (ems in selected_ems) {
    emsvars <- c(emsvars, paste0(emsvars_temp, ems))
  }

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

  if (length(selected_ems > 1)) {
    groupvars <- c(groupvars, "outcome", "Date", "isolation_success")

    subdat <- subdat %>%
      dplyr::group_by_at(.vars = groupvars) %>%
      dplyr::summarize(value = sum(value)) %>%
      mutate(region = "central")
  }

  ### what time point to select?
  tempdat <- subdat %>%
    filter(Date >= evaluation_window[1] & Date <= evaluation_window[2]) %>%
    select(-c(time, sample_num, scen_num, run_num)) %>%
    group_by(Date, d_As_ct1, reduced_inf_of_det_cases, isolation_success, time_to_detection, outcome) %>%
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
    dplyr::group_by(d_As_ct1, isolation_success, time_to_detection, outcome) %>%
    mutate(
      diff = value.mean - lag(value.mean),
      growthRate = (value.mean - lag(value.mean)) / lag(value.mean),
      mean_growthRate = mean(growthRate, na.rm = T)
    )

  return(tempdat)
}

#f_heatmap
f_heatmap <- function(df, selected_outcome, valuetype = "absolute") {
  #'  f_heatmap  performs a linea regression between contact tracing parameter and draws a heatmap using the model predicted values
  #' The function returns a list of the heatmap plot, and the thresholds used to draw the lines, as well as the filtered lm prediction dataset
  #' @param df  dataset
  #' @param selected_outcome  name of the outcome variable 
  #' @param valuetype  default "absolute", another option would be "growthRate"


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

  if (ems %in% names(regions)) {
    ems <- as.numeric(regions[[ems]])
  }


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
    customThemeNoFacet +
    scale_x_continuous(breaks = seq(0, 1, 0.2), labels = seq(0, 1, 0.2) * 100, expand = c(0, 0)) +
    scale_y_continuous(breaks = seq(0, 1, 0.2), labels = seq(0, 1, 0.2) * 100, expand = c(0, 0))

  xnew <- seq(0, 1, 0.2)
  ynew <- seq(0, 1, 0.2)
  # ...calculating prediction
  heatmap_threshold <- expand.grid(x = xnew, y = ynew)
  heatmap_threshold$z <- predict(xyzmodel, newdata = heatmap_threshold)
  heatmap_threshold <- heatmap_threshold %>%
    filter(z <= threshold) %>%
    dplyr::group_by(x) %>%
    dplyr::summarize(ythreshold = min(y))


  out_list <- list(matdatp, xyzmodel, heatmap_threshold, matdat)


  return(out_list)
}

#region_to_fct
region_to_fct <- function(dat, geography) {
  #' Helper function to convert region character variable to factor variable
  #' @param dat  dataset
  #' @param geography  level of analysis EMS or Region (aggregated or not)

  
  if (geography == "EMS") {
    levels <- c(1:11)
    labels <- paste0("EMS ", levels)
  }
  
  if (geography == "Region") {
    levels <- c(names(regions)[5], names(regions)[-5])
    labels <- stringr::str_to_title(levels)
  }
  
  dat$region <- factor(dat$region,
                       levels = levels,
                       labels = labels
  )
  return(dat)
}

### Load and subset files to save memory
nexpsfiles <- list.files(file.path(ct_dir, simdate), pattern = "trajectoriesDat.csv", recursive = TRUE, full.names = TRUE)
trajectoriesDat <- sapply(nexpsfiles, read.csv, simplify = FALSE) %>%
  bind_rows(.id = "id") 

trajectoriesDat <- subset(trajectoriesDat, time >= 100 & time <= 300)


## Parameter combinations that did run
sink(file.path(exp_dir, "parameter_combinations.txt"))
  cat("\ntable(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)")
  table(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
  cat("\ntable(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)")
  table(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
sink()


##--------------------------------------------
## Generate heatmap and supplementary plots per EMS or aggregated region
##--------------------------------------------
geography="EMS"
#geography <- "Region"
if (geography == "EMS") emsregions <- c(1:11)
if (geography == "Region") emsregions <- names(regions)

for (ems in emsregions) {
  # ems <- emsregions[1]
  ems_dir <- file.path(exp_dir, paste0(geography, "_", ems))
  if (!dir.exists(ems_dir)) dir.create(ems_dir)

  if (geography == "Region") {
    selected_ems <- as.numeric(regions[[ems]])
  } else {
    selected_ems <- ems
  }

  capacity <- load_capacity(selected_ems)
  capacity$deaths <- 0


  tempdat <- getdata(selected_ems)
  tempdat$region <- ems
  write.csv(tempdat, file.path(ems_dir, paste0(geography, "_", ems, "_dat.csv")))

  ### Thresholds from predictions
  thresholdDat <- list()
  ### Thresholds from linear model
  h_thresholdDat <- list()

  for (selected_outcome in c("critical", "hospitalized", "deaths", "ventilators")) {
    # selected_outcome = "critical"

    capacityline <- as.numeric(capacity[colnames(capacity) == selected_outcome])

    if (selected_outcome == "ventilators") {
      plotdat <- tempdat %>%
        filter(outcome == "crit_det") %>%
        mutate(value.mean = value.mean * 0.660) %>%
        as.data.frame()

      threshold_param <- plotdat %>%
        filter(Date == max(Date)) %>%
        filter(outcome == "crit_det") %>%
        mutate(value.mean = value.mean * 0.660) %>%
        mutate(
          capacity = capacityline,
          outcome = selected_outcome
        ) %>%
        filter(value.mean <= capacity) %>%
        group_by(d_As_ct1, time_to_detection) %>%
        filter(isolation_success == min(isolation_success)) %>%
        dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
    } else {
      plotdat <- tempdat %>%
        filter(outcome == selected_outcome) %>%
        as.data.frame()

      threshold_param <- plotdat %>%
        filter(Date == max(Date)) %>%
        mutate(capacity = capacityline) %>%
        filter(outcome == selected_outcome) %>%
        filter(value.mean <= capacity) %>%
        group_by(d_As_ct1, time_to_detection) %>%
        filter(isolation_success == min(isolation_success)) %>%
        dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
    }

    thresholdDat[[selected_outcome]] <- threshold_param


    l_plot <- ggplot(data = plotdat) + theme_cowplot() +
      # geom_vline(xintercept=as.Date("2020-08-02"), linetype="dashed")+
      geom_line(aes(x = Date, y = value.mean, group = interaction(isolation_success, d_As_ct1)), size = 1.3, col = "deepskyblue4") +
      facet_wrap(~time_to_detection) +
      labs(
        title = paste0(geography, " ", unique(plotdat$region)),
        caption = "each lines represents an unique combinations of isolation success and detection rate",
        subtitle = "test delay (days)", y = selected_outcome
      )
    
    ggsave(paste0(geography, "_", ems, "_", selected_outcome, "_line.png"),
           plot = l_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "png"
    )
    
    
    
    # selected_outcome = "critical"
    p_plot <- ggplot(data = subset(plotdat, Date == max(plotdat$Date))) + 
      theme_cowplot() +
      geom_point(aes(x = d_As_ct1, y = value.mean, col = isolation_success, shape = as.factor(time_to_detection)), size = 2.3) +
      labs(
        title = paste0(geography, " ", unique(tempdat$region)),
        subtitle = paste0("Time point: ",  evaluation_window[2],
                          "\nContact tracing start: ", evaluation_window[1]),
        shape = "test delay (days)",
        x = "detection rate (P, As, Sym)",
        y = selected_outcome
      ) +
      scale_color_viridis(option = "D", discrete = FALSE, direction = -1) +
      geom_hline(yintercept = capacityline, linetype = "dashed")
    
    ggsave(paste0(geography, "_", ems, "_", selected_outcome, "_scatter.png"),
           plot = p_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "png"
    )
    
    
    ### Line plot filtered with threshold value and heatmap
    if(dim(threshold_param)[1]==0) next
    threshold_param <- threshold_param %>% 
      mutate(threshold=1) %>%
      dplyr::select(-c(outcome,  value.mean, capacity ))
    
    testdat <- plotdat %>%  
      left_join(threshold_param, by=c("region", "time_to_detection", "d_As_ct1","isolation_success")) %>%
      dplyr::filter(threshold == 1 )
    
    l_plot2 <- ggplot(data = subset(testdat, d_As_ct1=min(d_As_ct1) )) + theme_cowplot() +
      geom_line(aes(x = Date, y = value.mean,col=isolation_success,
                    group=interaction(isolation_success)), size = 1.3) +
      facet_wrap(~time_to_detection) +
      geom_hline(yintercept = capacityline, linetype = "dashed")+
      labs(
        title = paste0(geography, " ", unique(plotdat$region)),
        subtitle = paste0("Outcome: ",selected_outcome, 
                          "\nMinimum detection rate ", round( unique(testdat$d_As_ct1),3)), 
        y = selected_outcome
      )+
      customThemeNoFacet+
      theme(axis.text.x  = element_text(size = 12, angle=60, hjust=1, vjust=1)) +
      scale_color_viridis(option = "D", discrete = FALSE, direction = -1) 
    
    ggsave(paste0(geography, "_", ems, "_", selected_outcome, "_line_belowCapacity.png"),
           plot = l_plot2, path = file.path(ems_dir), width = 14, height = 5, dpi = 300, device = "png"
    )


    for (testDelay in unique(plotdat$time_to_detection)) {
      heatmap_out <- f_heatmap(subset(plotdat, Date == max(plotdat$Date) &  time_to_detection == testDelay), selected_outcome, valuetype = "absolute")
      h_plot <- heatmap_out[[1]]
      h_threshold <- heatmap_out[[3]]
      ggsave(paste0(geography, "_", ems, "_", selected_outcome, "_tD", testDelay, "_heatmap.png"),
        plot = h_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "png"
      )
      ggsave(paste0(geography, "_", ems, "_", selected_outcome, "_tD", testDelay, "_heatmap.pdf"),
        plot = h_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "pdf"
      )
      rm(h_plot)
      if (dim(h_threshold)[1] != 0) {
        h_threshold$time_to_detection <- testDelay
        h_threshold$outcome <- selected_outcome
        h_threshold$region <- ems
        h_thresholdDat[[length(h_thresholdDat) + 1]] <- h_threshold
      }
    }
  }

  thresholdDat <- do.call(rbind.data.frame, thresholdDat)
  write.csv(thresholdDat, file.path(ems_dir, paste0(geography, "_", ems, "_thresholds.csv")))
  h_thresholdDat <- do.call(rbind.data.frame, h_thresholdDat)
  write.csv(h_thresholdDat, file.path(ems_dir, paste0(geography, "_", ems, "_lm_thresholds.csv")))
  
}


##--------------------------------------------
#### Summary plot of thresholds per region
##--------------------------------------------

### Load thresholds from lm model
thresholdsfiles <- list.files(file.path(exp_dir), pattern = "thresholds", recursive = TRUE, full.names = TRUE)
thresholdsfiles <- thresholdsfiles[grep(geography, thresholdsfiles)]
thresholdsfiles <- thresholdsfiles[grep("lm", thresholdsfiles)]

lmthresholdsDat <- sapply(thresholdsfiles, read.csv, simplify = FALSE) %>%
  bind_rows(.id = "id") %>%
  dplyr::select(-X) %>%
  dplyr::mutate(
    region = as.character(region),
    outcome = as.character(outcome)
  ) %>%
  dplyr::rename(d_As_ct1 = x, isolation_success = ythreshold)

lmthresholdsDat <- region_to_fct(lmthresholdsDat, geography)

### Load thresholds from predictions
thresholdsfiles <- list.files(file.path(exp_dir), pattern = "thresholds", recursive = TRUE, full.names = TRUE)
thresholdsfiles <- thresholdsfiles[grep(geography, thresholdsfiles)]
thresholdsfiles <- thresholdsfiles[!grepl("lm", thresholdsfiles)]

thresholdsDat <- sapply(thresholdsfiles, read.csv, simplify = FALSE) %>%
  bind_rows(.id = "id") %>%
  dplyr::select(-X) %>%
  mutate(
    region = as.character(region),
    outcome = as.character(outcome),
    outcome = factor(outcome,
      levels = c("hospitalized", "critical", "ventilators", "deaths"),
      labels = c("hospitalized", "critical", "ventilators", "deaths")
    ),
    capacityLabel = paste0("Capacity: ", capacity)
  )

thresholdsDat <- region_to_fct(thresholdsDat, geography)

table(thresholdsDat$region)
table(thresholdsDat$region, thresholdsDat$d_As_ct1)

capacityText <- thresholdsDat %>%
  select(region, outcome, capacityLabel) %>%
  unique()

if (geography == "Region") {
  pplot <- ggplot(data = subset(thresholdsDat, outcome != "deaths")) + theme_bw() +
    geom_jitter(aes(x = d_As_ct1, y = isolation_success, col = as.factor(time_to_detection)), size = 3) +
    geom_text(data = capacityText, aes(x = 0.18, y = 1, label = capacityLabel), col = "black") +
    geom_smooth(aes(x = d_As_ct1, y = isolation_success), se = FALSE, method = "lm", col = "darkgrey", size = 1) +
    geom_smooth(data = subset(lmthresholdsDat, outcome != "deaths"), aes(x = d_As_ct1, y = isolation_success), se = FALSE, method = "lm", col = "black", size = 1) +
    facet_grid(outcome ~ region) +
    labs(
      color = "test delay",
      x = "detection rate",
      y = "isolation success",
      caption = "\n dots from prediction dataset\ngrey line: thresholds from prediction dataset\nblack line: thresholds from linear model"
    ) +
    scale_color_brewer(palette = "Dark2") +
    customThemeNoFacet +
    theme(
      panel.grid.minor.x = element_blank(),
      panel.grid.minor.y = element_blank()
    ) +
    scale_x_continuous(labels = seq(0, 1, 0.2), breaks = seq(0, 1, 0.2)) +
    scale_y_continuous(labels = seq(0, 1, 0.2), breaks = seq(0, 1, 0.2))


  ggsave(paste0(geography, "_capacity_thresholds.png"),
    plot = pplot, path = file.path(exp_dir), width = 16, height = 9, dpi = 300, device = "png"
  )
}
if (geography == "EMS") {
  for (ems in unique(thresholdsDat$region)) {
    pplot <- ggplot(data = subset(thresholdsDat, region %in% ems & outcome != "deaths")) + theme_bw() +
      geom_jitter(aes(x = d_As_ct1, y = isolation_success, col = as.factor(time_to_detection)), size = 3) +
      geom_text(data = subset(capacityText, region %in% ems), aes(x = 0.18, y = 1, label = capacityLabel), col = "black") +
      geom_smooth(aes(x = d_As_ct1, y = isolation_success), se = FALSE, method = "lm", col = "darkgrey", size = 1) +
      geom_smooth(data = subset(lmthresholdsDat, region %in% ems & outcome != "deaths"), aes(x = d_As_ct1, y = isolation_success), se = FALSE, method = "lm", col = "black", size = 1) +
      facet_grid(outcome ~ region) +
      labs(
        color = "test delay",
        x = "detection rate",
        y = "isolation success",
        caption = "\n dots from prediction dataset\ngrey line: thresholds from prediction dataset\nblack line: thresholds from linear model"
      ) +
      scale_color_brewer(palette = "Dark2") +
      customThemeNoFacet +
      theme(
        panel.grid.minor.x = element_blank(),
        panel.grid.minor.y = element_blank()
      ) +
      scale_x_continuous(labels = seq(0, 1, 0.2), breaks = seq(0, 1, 0.2)) +
      scale_y_continuous(labels = seq(0, 1, 0.2), breaks = seq(0, 1, 0.2))


    ggsave(paste0(ems, "_capacity_thresholds.png"),
      plot = pplot, path = file.path(exp_dir), width = 6, height = 10, dpi = 300, device = "png"
    )
  }
}

thresholdsDat$method <- "simulations"
lmthresholdsDat$method <- "linear_model"

thresholdsDat %>%
  dplyr::select(colnames(lmthresholdsDat)) %>%
  rbind(lmthresholdsDat) %>%
  dplyr::select(-id) %>%
  pivot_wider(names_from = method, values_from = isolation_success) %>%
  write.csv(file.path(exp_dir, paste0(geography, "_Thresholds.csv")))

