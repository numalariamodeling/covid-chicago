## ==================================================
# R script that analysis trajectoriesDat
## ==================================================

require(tidyverse)
require(cowplot)
require(scales)


source("load_paths.R")
source("processing_helpers.R")

datadir <- file.path(data_path, "covid_chicago/NMH/")

# exp_name ="20200414_NMH_catchment_testInterventionStop_rn50"
exp_name <- "20200415_NMH_catchment_testInterventionStop_rn38"

startDate <- as.Date("2020-02-28")
interventionStart <- as.Date("2020-3-13")

## add data
dat <- read_csv(file.path(datadir, "Modeling COVID Data NMH_v1_200415_jg.csv"))
colnames(dat) <- gsub(" ", "_", colnames(dat))
dat <- dat %>%
  rename(Date = date) %>%
  mutate(Date = as.Date(Date, format = "%m/%d/%Y"))

## load predictions
trajectoriesDat <- read.csv(file.path(projectdir, "_temp/", exp_name, "/trajectoriesDat.csv"), header = TRUE)


head(trajectoriesDat)
table(trajectoriesDat$backtonormal_multiplier)
table(trajectoriesDat$stop_date)

### add time
trajectoriesDat$Date <- as.Date(trajectoriesDat$time + startDate)
trajectoriesDat$effectVar <- (1 - trajectoriesDat$backtonormal_multiplier) * 100

### Calculate new infections
### Aggregate seeds and samples
aggrDat_exposed <- trajectoriesDat %>% f_aggrDat(groupVars = c("time", "Date", "backtonormal_multiplier", "effectVar", "stop_date"), valueVar = "exposed", WideToLong = FALSE)
aggrDat_hosp_cumul <- trajectoriesDat %>% f_aggrDat(groupVars = c("time", "Date", "backtonormal_multiplier", "effectVar", "stop_date"), valueVar = "hosp_cumul", WideToLong = FALSE)


## Show social multiploer arrows
# mean1 <- mean(c(0.9, 1))
# mean2 <- mean(c(0.6, 0.9))
# mean3 <- mean(c(0.05 , 0.3))
# =data.frame(x=c(as.Date("2020-03-13"),as.Date("2020-03-17"),as.Date("2020-03-21")), y=c(80000*mean1,80000*mean2,80000*mean3))

f_plot_fixDate <- function(data, maxtime, ylabel, effectVar, stopDate = NULL, getLegend = F) {
  if (is.null(stopDate)) interventionEnd <- as.Date("2020-05-30")
  if (!is.null(stopDate)) interventionEnd <- as.Date(stopDate)

  pplot <- ggplot(data = subset(data, time < maxtime & stop_date == stopDate)) + theme_cowplot() +
    # geom_segment(data=d, mapping=aes(x=x, y=y, xend=x, yend=y-10000), arrow=arrow(), size=1.7, color="black") +
    annotate("rect",
      fill = "grey", alpha = 0.3,
      xmin = interventionStart, xmax = as.Date(stopDate),
      ymin = -Inf, ymax = Inf
    ) +
    geom_ribbon(aes(x = Date, ymin = q2.5, ymax = q97.5, group = effectVar), alpha = 0.2, fill = "grey") +
    geom_ribbon(aes(x = Date, ymin = q25, ymax = q75, fill = as.factor(effectVar)), alpha = 0.5) +
    geom_line(aes(
      x = Date, y = median.val,
      col = as.factor(effectVar),
      group = effectVar
    ), size = 1.7) +
    labs(
      x = "",
      y = ylabel,
      col = "Maintained reduction in Ki (%)",
      fill = "Maintained reduction in Ki (%)"
    ) +
    theme(legend.position = "right") +
    scale_color_brewer(palette = "Dark2") +
    scale_fill_brewer(palette = "Dark2") +
    customTheme_noAngle +
    facet_wrap(~stop_date) +
    geom_vline(xintercept = as.Date(stopDate)) +
    geom_vline(xintercept = as.Date("2020-04-15"), col = "red") +
    facet_wrap(~stop_date, nrow = 1) +
    scale_y_continuous(lim = c(0, 150000), labels = comma) +
    scale_x_date(labels = date_format("%b"), date_breaks = "1 month", )

  legend <- get_legend(pplot)
  pplot <- pplot + theme(legend.position = "none")
  if (getLegend) out <- legend
  if (getLegend == F) out <- pplot

  return(out)
}



table(trajectoriesDat$stop_date)
table(trajectoriesDat$effectVar)
aggrDat_exposed$stop_date <- as.Date(aggrDat_exposed$stop_date)
aggrDat_hosp_cumul$stop_date <- as.Date(aggrDat_hosp_cumul$stop_date)

p1a <- f_plot_fixDate(subset(aggrDat_hosp_cumul, stop_date == as.Date("2020-04-30")), 180, "hosp_det_cumul", effectVar = "effectVar", "2020-04-30")
p1b <- f_plot_fixDate(subset(aggrDat_hosp_cumul, stop_date == as.Date("2020-05-30")), 180, "hosp_det_cumul", effectVar = "effectVar", "2020-05-30")
p1c <- f_plot_fixDate(subset(aggrDat_hosp_cumul, stop_date == as.Date("2020-06-30")), 180, "hosp_det_cumul", effectVar = "effectVar", "2020-06-30")
p1d <- f_plot_fixDate(subset(aggrDat_hosp_cumul, stop_date == as.Date("2020-07-30")), 180, "hosp_det_cumul", effectVar = "effectVar", "2020-07-30")
legend <- f_plot_fixDate(subset(aggrDat_hosp_cumul, stop_date == as.Date("2020-07-30")), 180, "hosp_det_cumul", effectVar = "effectVar", "2020-07-30", getLegend = T)

## add data


pall <- plot_grid(p1a, p1b, p1c, p1d)
(pout <- plot_grid(pall, legend, rel_widths = c(1, 0.3)))

# ggsave("interventionStop_NMH_catchment_exposed.png")
p1a <- p1a + geom_point(data = dat, aes(x = Date, y = cumulative_admissions), size = 3) + scale_y_log10()



ggplot(data = subset(aggrDat_hosp_cumul, time < 200)) + theme_cowplot() +
  # geom_segment(data=d, mapping=aes(x=x, y=y, xend=x, yend=y-10000), arrow=arrow(), size=1.7, color="black") +
  geom_ribbon(aes(x = Date, ymin = q2.5, ymax = q97.5, group = interaction(effectVar, stop_date)), alpha = 0.2, fill = "grey") +
  geom_ribbon(aes(x = Date, ymin = q25, ymax = q75, fill = as.factor(effectVar), group = interaction(effectVar, stop_date)), alpha = 0.5) +
  geom_line(aes(
    x = Date, y = median.val,
    col = as.factor(effectVar),
    group = interaction(effectVar, stop_date)
  ), size = 1.7) +
  labs(
    x = "",
    y = "hosp_cumul",
    col = "Maintained reduction in Ki (%)",
    fill = "Maintained reduction in Ki (%)"
  ) +
  theme(legend.position = "right") +
  scale_color_brewer(palette = "Dark2") +
  scale_fill_brewer(palette = "Dark2") +
  customTheme_noAngle +
  scale_y_continuous(lim = c(0, 150000), labels = comma) +
  scale_x_date(labels = date_format("%b"), date_breaks = "1 month") +
  geom_point(data = dat, aes(x = Date, y = cumulative_admissions), size = 3) + scale_y_log10() +
  facet_wrap(~stop_date) +
  geom_vline(xintercept = as.Date("2020-04-15"), col = "red")
