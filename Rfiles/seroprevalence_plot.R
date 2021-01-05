
library(tidyverse)
library(data.table)
library(cowplot)
library(lubridate)

theme_set(theme_minimal())


runInBatchMode <- TRUE

if (runInBatchMode) {
  cmd_agrs <- commandArgs()
  length(cmd_agrs)
  exp_name <- cmd_agrs[length(cmd_agrs) - 2]
  Location <- cmd_agrs[length(cmd_agrs) - 1]
  workingDir <- cmd_agrs[length(cmd_agrs)]
} else {
  exp_name <- "20201215_IL_mr_test_run2"
  Location <- "Local"
  workingDir <- getwd()
}

print(workingDir)
source(file.path(workingDir, "load_paths.R"))

### Set custom theme for plotting
fontscl <- 3
customTheme <- theme(
  strip.text.x = element_text(size = 12 + fontscl, face = "bold"),
  strip.text.y = element_text(size = 12 + fontscl, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 16 + fontscl, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 14 + fontscl),
  plot.caption = element_text(size = 10 + fontscl),
  legend.title = element_text(size = 12 + fontscl),
  legend.text = element_text(size = 12 + fontscl),
  axis.text.x = element_text(size = 11 + fontscl),
  axis.text.y = element_text(size = 11 + fontscl),
  axis.title.x = element_text(size = 12 + fontscl),
  axis.title.y = element_text(size = 12 + fontscl)
)


#### Load prevalence dat generated from plot_prevalence.py
plot_dir <- file.path(simulation_output, exp_name, "_plots")
dat <- fread(file.path(simulation_output, exp_name, "prevalenceDat.csv"))


### Transform dataformat
modelCols <- c("date", "scen_num", "run_num", "sample_num")
prevCols <- colnames(dat)[grep("prev", colnames(dat))]
keepCols <- c(modelCols, prevCols)
dat <- dat %>%
  select_at(keepCols) %>%
  mutate(date = as.Date(date)) %>%
  rename_with(~ gsub("_All", "_EMS-0", .x)) %>%
  pivot_longer(cols = -c(modelCols)) %>%
  separate(name, into = c("channel", "region"), sep = "_EMS-") %>%
  mutate(value = value * 100) %>%
  group_by(date, region, channel) %>%
  summarize(
    min.value = min(value, na.rm = TRUE),
    max.value = max(value, na.rm = TRUE),
    median.value = median(value, na.rm = TRUE),
    q25.value = quantile(value, probs = 0.25, na.rm = TRUE),
    q75.value = quantile(value, probs = 0.75, na.rm = TRUE),
    q2.5.value = quantile(value, probs = 0.025, na.rm = TRUE),
    q97.5.value = quantile(value, probs = 0.975, na.rm = TRUE)
  ) %>%
  filter(channel == "seroprevalence") %>%
  mutate(region = as.numeric(region)) %>%
  arrange(region)


dat$region <- factor(dat$region,
  levels = c(0:11),
  labels = c("IL", c(1:11))
)

#### Generate plot
date_label_short <- paste0(format(Sys.Date(), "%b")," ", day(Sys.Date()))
date_label_long <- paste0(format(Sys.Date(), "%B")," ", day(Sys.Date()))

pplot_top <- ggplot(data = subset(dat, region == "IL")) +
  geom_ribbon(aes(x = date, ymin = q2.5.value, ymax = q97.5.value), alpha = 0.3, fill = "#f77189") +
  geom_ribbon(aes(x = date, ymin = q25.value, ymax = q75.value), alpha = 0.4, fill = "#f77189") +
  geom_line(aes(x = date, y = median.value), color = "#f77189", size = 1) +
  geom_text(aes(x = Sys.Date()+20, y = max(dat$median.value) * 0.98 ,label = date_label_short), size = 5, color='#666666') +
  scale_x_date(date_breaks = "30 days", date_labels = "%b", expand = c(0, 0)) +
  labs(
    title = "Model predictions for Illinois over time\n",
    x = paste0("\n Months in 2020 to 2021"),
    y = "Fraction ever infected (%)\n"
  ) +
  geom_vline(xintercept = Sys.Date(), linetype = "dashed", color='#666666') +
  geom_hline(yintercept = c(Inf, -Inf)) +
  geom_vline(xintercept = c(Inf, -Inf)) +
  theme(
    legend.position = "none",
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank()
  ) +
  customTheme

dat_today <- dat %>% filter(date == Sys.Date())

pplot_bottom <- ggplot(data = subset(dat_today, region == "IL")) +
  geom_rect(aes(xmin = -Inf, xmax = Inf, ymin = q2.5.value, ymax = q97.5.value), fill = "grey", alpha = 0.3) +
  geom_rect(aes(xmin = -Inf, xmax = Inf, ymin = q25.value, ymax = q75.value), fill = "grey", alpha = 0.4) +
  geom_hline(aes(yintercept = median.value), linetype = "longdash") +
  geom_pointrange(
    data = subset(dat_today, region != "IL"),
    aes(x = region, y = median.value, ymin = q2.5.value, ymax = q97.5.value), color = "#f77189"
  ) +
  geom_text(aes(x = 1.4, y = median.value + 2, label = "Illinois overall"), size = 5, color='#666666') +
  labs(
    title = paste0("Model predictions per COVID-19 Region for ", date_label_long, "\n"),
    y = "Fraction ever infected (%)\n", x = "\nCOVID-19 Region"
  ) +
  geom_hline(yintercept = c(Inf, -Inf)) +
  geom_vline(xintercept = c(Inf, -Inf)) +
  theme(
    legend.position = "none",
    panel.grid.major.x = element_blank(),
    panel.grid.minor.x = element_blank(),
    axis.ticks = element_line()
  ) +
  customTheme

pplot <- plot_grid(pplot_top, pplot_bottom, ncol = 1)

plotname <- paste0("seroprevalence_IL_and_by_region_", gsub("-", "", Sys.Date()))
ggsave(paste0(plotname, ".png"), plot = pplot, path = plot_dir, width = 8, height = 10, device = "png")
ggsave(paste0(plotname, ".pdf"), plot = pplot, path = file.path(plot_dir, "pdf"), width = 8, height = 10, device = "pdf")


### For text
sink(file.path(simulation_output, exp_name, paste0("seroprevalence_",gsub("-", "", Sys.Date()),".txt")))
print(Sys.Date())
print(dat_today)
sink()
