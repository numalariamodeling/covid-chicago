## -----------------------------------------------------------------------------------
#### Plot Rt timeline with descriptions per region, using processed csv file for civs
## -----------------------------------------------------------------------------------

library(tidyverse)
library(data.table)
library(cowplot)


runInBatchMode <- TRUE

if (runInBatchMode) {
  cmd_agrs <- commandArgs()
  length(cmd_agrs)
  workingDir <- cmd_agrs[length(cmd_agrs)]
} else {
  today <- Sys.Date()
  workingDir <- getwd() ## Location of gitrepository covid-chicago/Rfiles
}

print(workingDir)
source(file.path(workingDir, "load_paths.R"))


NU_civis_outputs <- file.path(project_path, "NU_civis_outputs/")

today <- Sys.Date()
NUdirs <- list.files(NU_civis_outputs)
simdate <- NUdirs[length(NUdirs)]
simdate_lastweek <- NUdirs[length(NUdirs) - 1]

outdir <- file.path(project_path, "NU_cdph_outputs", simdate)
if (!dir.exists(outdir)) dir.create(outdir)

customTheme <- theme(
  strip.text.x = element_text(size = 14, face = "bold"),
  plot.title = element_text(size = 14),
  plot.subtitle = element_text(size = 12),
  plot.caption = element_text(size = 10, hjust = 0),
  legend.title = element_text(size = 14),
  legend.text = element_text(size = 12),
  axis.title.x = element_text(size = 14),
  axis.text.x = element_text(size = 12),
  axis.title.y = element_text(size = 14),
  axis.text.y = element_text(size = 12)
)


f_generateTimeline_plot <- function(selected_region, addLastWeek = T, plot_stop_date = today,
                                    changepoint1 = as.Date("2020-09-17"),
                                    changepoint2 = as.Date("2020-10-10")) {
  plot_title <- gsub("covidregion_", "Region ", selected_region)
  if (selected_region == "covidregion_11") plot_title <- "Chicago"

  dat <- fread(file.path(NU_civis_outputs, paste0(simdate, "/csv/nu_", simdate, ".csv"))) %>%
    mutate(date = as.Date(as.character(date), format = "%Y-%m-%d")) %>%
    filter(scenario_name=="baseline",
      geography_modeled == selected_region,
      date <= as.Date(plot_stop_date)
    )

  (currentRt <- dat %>% filter(date == today) %>% dplyr::select(rt_median, rt_lower, rt_upper))
  (initialRt_worst <- dat %>% filter(date <= as.Date("2020-03-15")) %>% dplyr::summarize(rt_median = max(rt_median), rt_lower = min(rt_lower), rt_upper = max(rt_upper))) ## select worst case widest uncertaiity in past
  (initialRt_mean <- dat %>% filter(date <= as.Date("2020-03-15")) %>% dplyr::summarize(rt_median = mean(rt_median), rt_lower = mean(rt_lower), rt_upper = mean(rt_upper))) ## select mean


  p1 <- ggplot(data = dat) +
    theme_cowplot() +
    background_grid() +
    geom_vline(xintercept = c(changepoint1, changepoint2), col = "grey15", linetype = "dotted", size = 0.8, alpha = 0.8) +
    geom_hline(yintercept = Inf) +
    geom_vline(xintercept = Inf) +
    geom_hline(yintercept = 1) +
    geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue4", alpha = 0.3) +
    geom_line(aes(x = date, y = rt_median), col = "deepskyblue4", size = 1) +
    labs(
      title = plot_title,
      subtitle = paste0("Estimated Rt using NU's COVID-19 transmission model \nEstimated Rt for Oct 21th: ", round(currentRt$rt_median, 3), " (95%CI: ", round(currentRt$rt_lower, 3), " - ", round(currentRt$rt_upper, 3), ")"),
      x = "", caption = paste0("Fitting point: Time in the simulation model at which the transmission rate is changed to match the observed data trends (~ 1 fitting point per month)\nModel fitted to hospital inpatient census, intensive care unit census data and reported deaths\nRt estimated based on predicted new infections using EpiEstim with an uncertain SI distribution\nLag time between infections and hospitalizations and selected fitting points affect estimated Rt for the previous weeks\nPlot truncated in March, before March 15th Rt was estimated at ", round(initialRt_worst$rt_median, 3), " (95%CI: ", round(initialRt_worst$rt_lower, 3), " - ", round(initialRt_worst$rt_upper, 3), ")\n"),
      y = expr(italic(R[t]))
    ) +
    scale_x_date(date_breaks = "30 days", date_labels = "%b", expand = c(0, 0)) +
    scale_y_continuous(lim = c(0.7, 1.5), labels = seq(0.7, 1.5, 0.1), breaks = seq(0.7, 1.5, 0.1)) +
    customTheme +
    annotate("text", x = changepoint1, y = 1.4, label = "fitting\npoint", col = "grey10", size = 4, alpha = 0.8) +
    annotate("text", x = changepoint2, y = 1.4, label = "fitting\npoint", col = "grey10", size = 4, alpha = 0.8)


  if (plot_stop_date > today) {
    future_textpoint <- plot_stop_date - 10
    p1 <- p1 + geom_rect(xmin = as.Date(today), xmax = Inf, ymin = -Inf, ymax = Inf, fill = "grey", alpha = 0.01) +
      annotate("text", x = future_textpoint, y = 1.4, label = "future prediction\nif current trend continues", col = "grey15", size = 4, alpha = 0.5)
  }

  if (addLastWeek) {
    dat_lastweek <- fread(file.path(NU_civis_outputs, paste0(simdate_lastweek, "/csv/nu_", simdate_lastweek, ".csv"))) %>%
      filter(scenario_name=="baseline", 
             geography_modeled == selected_region)

    dat_lastweek$date <- as.Date(as.character(dat_lastweek$date), format = "%Y-%m-%d")
    dat_lastweek <- dat_lastweek %>% filter(date <= plot_stop_date)

    ythisweek <- dat$rt_median[dat$date == max(dat$date)]
    ylastweek <- dat_lastweek$rt_median[dat_lastweek$date == max(dat_lastweek$date)]

    p1 <- p1 + geom_line(data = dat_lastweek, aes(x = date, y = rt_median), col = "deepskyblue4", size = 1, linetype = "dashed", alpha = 0.5) +
      geom_ribbon(data = dat_lastweek, aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue4", alpha = 0.1) +
      annotate("text", x = today - 15, y = ylastweek - 0.02, label = "last week's fit", col = "deepskyblue4", size = 4, alpha = 0.5) +
      annotate("text", x = today - 15, y = ythisweek - 0.02, label = "this week's fit", col = "deepskyblue4", size = 4, alpha = 0.9)
  }


  ggsave(paste0(simdate, "_Rt_", selected_region, ".png"),
    plot = p1, path = file.path(outdir), width = 10, height = 6, device = "png"
  )
  ggsave(paste0(simdate, "_Rt_", selected_region, ".pdf"),
    plot = p1, path = file.path(outdir), width = 10, height = 6, device = "pdf"
  )
}


#### Run function
selected_regions <- c("covidregion_10", "covidregion_11")
for (selected_region in selected_regions) {
  f_generateTimeline_plot(selected_region = selected_region)
}
