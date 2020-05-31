## ==================================================
# R script that analysis trajectoriesDat
## ==================================================

require(tidyverse)
require(cowplot)
require(scales)
require(lattice)
require(readxl)
require(viridis)
library(stringr)

gitdir <- file.path("C:/Users/mrung/gitrepos/covid-chicago")
datadir <- file.path("C:/Users/mrung/Box/NU-malaria-team/data")
projectdir <- file.path("C:/Users/mrung/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/contact_tracing/")

source(file.path(gitdir, "Rfiles/f_AggrDat.R"))
source(file.path(gitdir, "Rfiles/setup.R"))


regions <- list(
  "northcentral" = c(1, 2),
  "northeast" = c(7, 8, 9, 10, 11),
  "central" = c(3, 6),
  "southern" = c(4, 5),
  "illinois" = c(1:11)
)


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

  if (length(selected_ems) == 1) {
    capacity <- ems_df %>%
      filter(ems == selected_ems) %>%
      dplyr::select(hospitalized, critical, ventilators)
  } else {
    capacity <- ems_df %>%
      filter(ems %in% selected_ems) %>%
      dplyr::summarize(
        hospitalized = sum(hospitalized),
        critical = sum(critical),
        ventilators = sum(ventilators)
      )
  }

  return(capacity)
}

# exp_name ="20200414_NMH_catchment_testInterventionStop_rn50"
simdate <- "20200530"
reopeningdate <- as.Date("2020-06-01")
evaluation_window <- c(reopeningdate, reopeningdate + 60)


nexps <- list.files(file.path(projectdir, simdate))
if (length(nexps) == 1) {
  exp_name <- nexps
  exp_dir <- file.path(projectdir, simdate, exp_name)
} else {
  exp_name <- simdate
  exp_dir <- file.path(projectdir, simdate)
}


nexpsfiles <- list.files(file.path(projectdir, simdate), pattern = "trajectoriesDat.csv", recursive = TRUE, full.names = TRUE)
trajectoriesDat <- sapply(nexpsfiles, read.csv, simplify = FALSE) %>%
  bind_rows(.id = "id")

trajectoriesDat <- subset(trajectoriesDat, time >= 100 & time <= 300)


## load predictions
getdata <- function(selected_ems) {
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

  if (ems %in% names(regions)) {
    ems <- as.numeric(regions[[ems]])
  }

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
sink(file.path(exp_dir, "parameter_combinations.txt"))
cat("\ntable(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)")
table(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
cat("\ntable(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)")
table(trajectoriesDat$reduced_inf_of_det_cases, trajectoriesDat$time_to_detection)
sink()


runPerEMS=FALSE
if (runPerEMS) {
  for (ems in c(1:11)) {
    # ems <- 2
    ems_dir <- file.path(exp_dir, paste0("EMS_", ems))
    if (!dir.exists(ems_dir)) dir.create(ems_dir)

    capacity <- load_capacity(ems)
    capacity$deaths <- 0


    tempdat <- getdata(ems)
    tempdat$region <- ems
    write.csv(tempdat, file.path(ems_dir, paste0("EMS_", ems, "_dat.csv")))

    ### what time point to select?   - calculate mean over timeperiod ?
    ### Aggregate time for heatmap
    dfAggr <- tempdat %>%
      dplyr::select(-Date) %>%
      dplyr::group_by(region, d_As_ct1, isolation_success, time_to_detection, outcome) %>%
      dplyr::summarize_all(.funs = "mean", na.rm = T)

    thresholdDat <- list()
    for (selected_outcome in c("critical", "hospitalized", "deaths", "ventilators")) {
      # selected_outcome = "critical"

      capacityline <- as.numeric(capacity[colnames(capacity) == selected_outcome])

      if (selected_outcome == "ventilators") {
        plotdat <- tempdat %>%
          filter(outcome == "crit_det") %>%
          mutate(value.mean = value.mean * 0.660) %>%
          as.data.frame()

        threshold_param <- dfAggr %>%
          filter(outcome == "crit_det") %>%
          mutate(value.mean = value.mean * 0.660) %>%
          mutate(capacity = capacityline,
                 outcome=selected_outcome) %>%
          filter(value.mean <= capacity)
        group_by(d_As_ct1, time_to_detection) %>%
          filter(isolation_success == min(isolation_success)) %>%
          dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
      } else {
        plotdat <- tempdat %>%
          filter(outcome == selected_outcome) %>%
          as.data.frame()

        threshold_param <- dfAggr %>%
          mutate(capacity = capacityline) %>%
          filter(outcome == selected_outcome) %>%
          filter(value.mean <= capacity)
        group_by(d_As_ct1, time_to_detection) %>%
          filter(isolation_success == min(isolation_success)) %>%
          dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
      }

      thresholdDat[[selected_outcome]] <- threshold_param
      #write.csv(threshold_param, file.path(ems_dir, paste0("EMS_", ems, "_", selected_outcome, "_thresholds.csv")))


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
        ggsave(paste0("EMS_", ems, "_", selected_outcome, "_tD", testDelay, "_heatmap.pdf"),
               plot = h_plot, path = file.path(ems_dir), width = 8, height = 6, dpi = 300, device = "pdf"
        )
        rm(h_plot)
      }
    }
    
    thresholdDat <- do.call(rbind.data.frame, thresholdDat)
    write.csv(thresholdDat, file.path(ems_dir, paste0("EMS_", ems, "_thresholds.csv")))
  }
}
#### Extract minium value per ems and per outcome and plot + csv summary table


##### Aggregate per super region
runPerRegion=TRUE
if (runPerRegion) {
  for (region in names(regions)) {
    # region <- "central"
    region_dir <- file.path(exp_dir, paste0("Region_", region))
    if (!dir.exists(region_dir)) dir.create(region_dir)

    ems <- as.numeric(regions[[region]])
    capacity <- load_capacity(ems)
    capacity$deaths <- 0


    tempdat <- getdata(ems)
    tempdat$region <- region
    write.csv(tempdat, file.path(region_dir, paste0("Region_", region, "_dat.csv")))

    ### what time point to select?   - calculate mean over timeperiod ?
    ### Aggregate time for heatmap
    dfAggr <- tempdat %>%
      dplyr::select(-Date) %>%
      dplyr::group_by(region, d_As_ct1, isolation_success, time_to_detection, outcome) %>%
      dplyr::summarize_all(.funs = "mean", na.rm = T)

    thresholdDat <- list()
    for (selected_outcome in c("critical", "hospitalized", "deaths", "ventilators")) {
      # selected_outcome = "critical"

      capacityline <- as.numeric(capacity[colnames(capacity) == selected_outcome])

      if (selected_outcome == "ventilators") {
        plotdat <- tempdat %>%
          filter(outcome == "crit_det") %>%
          mutate(value.mean = value.mean * 0.660) %>%
          as.data.frame()

        threshold_param <- dfAggr %>%
          filter(outcome == "crit_det") %>%
          mutate(value.mean = value.mean * 0.660) %>%
          mutate(capacity = capacityline,
                 outcome=selected_outcome) %>%
          filter(value.mean <= capacity) %>%
          group_by(d_As_ct1, time_to_detection) %>%
          filter(isolation_success == min(isolation_success)) %>%
          dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
      } else {
        plotdat <- tempdat %>%
          filter(outcome == selected_outcome) %>%
          as.data.frame()

        threshold_param <- dfAggr %>%
          mutate(capacity = capacityline) %>%
          filter(outcome == selected_outcome) %>%
          filter(value.mean <= capacity) %>%
          group_by(d_As_ct1, time_to_detection) %>%
          filter(isolation_success == min(isolation_success)) %>%
          dplyr::select(region, d_As_ct1, isolation_success, time_to_detection, outcome, value.mean, capacity)
      }

      thresholdDat[[selected_outcome]] <- threshold_param
      #write.csv(threshold_param, file.path(ems_dir, paste0("EMS_", ems, "_", selected_outcome, "_thresholds.csv")))
      
      
      l_plot <- ggplot(data = plotdat) + theme_cowplot() +
        # geom_vline(xintercept=as.Date("2020-08-02"), linetype="dashed")+
        geom_line(aes(x = Date, y = value.mean, group = interaction(isolation_success, d_As_ct1)), size = 1.3, col = "deepskyblue4") +
        facet_wrap(~time_to_detection) +
        labs(
          title = paste0("Region ", unique(plotdat$region)),
          caption = "each lines represents an unique combinations of isolation success and detection rate",
          subtitle = "test delay (days)", y = selected_outcome
        )

      ggsave(paste0("Region_", region, "_", selected_outcome, "_line.png"),
        plot = l_plot, path = file.path(region_dir), width = 8, height = 6, dpi = 300, device = "png"
      )

      # selected_outcome = "critical"
      p_plot <- ggplot(data = subset(plotdat, Date >= as.Date("2020-08-01") & Date < as.Date("2020-08-03"))) + theme_cowplot() +
        geom_point(aes(x = d_As_ct1, y = value.mean, col = isolation_success, shape = as.factor(time_to_detection)), size = 2.3) +
        labs(
          title = paste0("Region ", unique(tempdat$region)),
          subtitle = "1 months after reopening",
          shape = "test delay (days)",
          x = "detection rate (P, As, Sym)",
          y = selected_outcome
        ) +
        scale_color_viridis(option = "D", discrete = FALSE, direction = -1) +
        geom_hline(yintercept = capacityline, linetype = "dashed")

      ggsave(paste0("region_", region, "_", selected_outcome, "_scatter.png"),
        plot = p_plot, path = file.path(region_dir), width = 8, height = 6, dpi = 300, device = "png"
      )


      for (testDelay in unique(dfAggr$time_to_detection)) {
        h_plot <- f_heatmap(subset(dfAggr, time_to_detection == testDelay), selected_outcome, valuetype = "absolute")
        ggsave(paste0("region_", region, "_", selected_outcome, "_tD", testDelay, "_heatmap.png"),
          plot = h_plot, path = file.path(region_dir), width = 8, height = 6, dpi = 300, device = "png"
        )
        ggsave(paste0("region_", region, "_", selected_outcome, "_tD", testDelay, "_heatmap.pdf"),
               plot = h_plot, path = file.path(region_dir), width = 8, height = 6, dpi = 300, device = "pdf"
        )
        rm(h_plot)
      }
    }
    thresholdDat <- do.call(rbind.data.frame, thresholdDat)
    write.csv(thresholdDat, file.path(region_dir, paste0("Region_", region, "_thresholds.csv")))
  }
}



thresholdsfiles <- list.files(file.path(exp_dir),pattern="thresholds",recursive=TRUE, full.names = TRUE)
thresholdsfiles <- thresholdsfiles[grep("Region",thresholdsfiles)]

thresholdsDat <- sapply(thresholdsfiles, read.csv, simplify = FALSE) %>%
  bind_rows(.id = "id") %>% 
  dplyr::select(-X) %>%
  mutate(outcome=as.character(outcome),
         outcome = factor(outcome, levels=c("hospitalized","critical","crit_det","deaths"),
                          labels=c("hospitalized","critical","ventilators","deaths")),
         capacityLabel = paste0("Capacity: ",capacity))


regionnames <-  c(names(regions)[5],names(regions)[-5])

thresholdsDat$region <- factor(thresholdsDat$region, 
                               levels=regionnames, 
                               labels= stringr::str_to_title(regionnames))

table(thresholdsDat$region)
table(thresholdsDat$region,thresholdsDat$d_As_ct1)

capacityText <- thresholdsDat %>% select(region, outcome, capacityLabel) %>% unique()


pplot <- ggplot(data=thresholdsDat) + theme_bw() +
  geom_jitter(aes(x=d_As_ct1, y=isolation_success,col=as.factor(time_to_detection)),size=3)+
  geom_text(data=capacityText,aes(x=0.18, y=1,label=capacityLabel),col="black")+
  geom_smooth(aes(x=d_As_ct1, y=isolation_success),se=FALSE, method="lm", col="grey",size=1)+
  facet_grid(outcome~region)+
  labs(color="test delay",x="detection rate", y="isolation success")+
  scale_color_manual(values=TwoCols)+
  customThemeNoFacet+
  theme(panel.grid.minor.x = element_blank(),
        panel.grid.minor.y = element_blank())+
  scale_x_continuous(labels=seq(0,1,0.2),breaks=seq(0,1,0.2))+
  scale_y_continuous(labels=seq(0,1,0.2),breaks=seq(0,1,0.2))

ggsave(paste0("capacity_thresholds.png"),
       plot = pplot, path = file.path(exp_dir), width = 16, height = 9, dpi = 300, device = "png"
)


write.csv(thresholdDat, file.path(exp_dir, paste0("Thresholds.csv")))




