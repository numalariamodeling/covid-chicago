## ==============================================================
## R script to plot the weekly deliverables together in one plot
## ==============================================================


require(tidyverse)
require(cowplot)
require(scales)

source("load_paths.R")
source("processing_helpers.R")


simdates <- c(  "20200902","20200910","20200916")
scenario <- "baseline" # june1partial10  , june1partial30

dat1 <- read_csv(file.path(project_path, paste0("NU_civis_outputs/", simdates[1], "/csv/nu_",  simdates[1], ".csv")))
dat2 <- read_csv(file.path(project_path, paste0("NU_civis_outputs/", simdates[2], "/csv/nu_",  simdates[2], ".csv")))
dat3 <- read_csv(file.path(project_path, paste0("NU_civis_outputs/", simdates[3], "/csv/nu_",  simdates[3], ".csv")))



dat1$simdate <- simdates[1]
dat2$simdate <- simdates[2]
dat3$simdate <- simdates[3]


dat2 <- dat2 %>%  dplyr::select(colnames(dat1))
dat1 <- dat1 %>%  dplyr::select(colnames(dat2))

dat <- dat1 %>%
  rbind( dat2) %>%
  rbind( dat3) %>%
  dplyr::mutate(date = as.Date(date)) %>%
  filter(
    date <= "2021-03-01",
    geography_modeled == "illinois"
  )

table(dat$simdate)

colnames(dat)
colnames(dat) <- gsub(" ",".",colnames(dat))
colnames(dat) <- gsub("-",".",colnames(dat))
colnames(dat)

legend <- get_legend(ggplot(data = dat) +
                       theme_cowplot() +
                       geom_ribbon(aes(
                         x = date, ymin = cases_new_lower,
                         ymax = cases_new_upper, fill = simdate
                       ), alpha = 0.3) +
                       geom_line(aes(x = date, y = cases_new_median, col = simdate), size = 1.3))


p1 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = date, ymin = cases_new_lower,
    ymax = cases_new_upper, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = date, y = cases_new_median, col = simdate), size = 1.3) +
  geom_vline(xintercept = as.Date("2020-08-05"), linetype = "dashed", color = "grey") +
  theme(legend.position = "none") +
  labs(y = "Covid-19 infections") +
  scale_y_continuous(labels = comma)


p2 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = date, ymin = vent_lower,
    ymax = vent_upper, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = date, y = vent_median, col = simdate), size = 1.3) +
  geom_vline(xintercept = as.Date("2020-08-05"), linetype = "dashed", color = "grey") +
  theme(legend.position = "none") +
  labs(y = "ventilators used") +
  scale_y_continuous(labels = comma)


p3 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = date, ymin = deaths_lower,
    ymax = deaths_upper, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = date, y = deaths_median, col = simdate), size = 1.3) +
  geom_vline(xintercept = as.Date("2020-08-05"), linetype = "dashed", color = "grey") +
  theme(legend.position = "none") +
  labs(y = "covid-19 deaths") +
  scale_y_continuous(labels = comma)


p4 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = date, ymin = hosp_bed_lower,
    ymax = hosp_bed_upper, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = date, y = hosp_bed_median, col = simdate), size = 1.3) +
  geom_vline(xintercept = as.Date("2020-08-05"), linetype = "dashed", color = "grey") +
  theme(legend.position = "none") +
  labs(y = "hospital beds occupied") +
  scale_y_continuous(labels = comma)


p5 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = date, ymin = icu_lower,
    ymax = icu_upper, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = date, y = icu_median, col = simdate), size = 1.3) +
  geom_vline(xintercept = as.Date("2020-08-05"), linetype = "dashed", color = "grey") +
  theme(legend.position = "none") +
  labs(y = "ICU beds occupied") +
  scale_y_continuous(labels = comma)


p6 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = date, ymin = recovered_lower,
    ymax = recovered_upper, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = date, y = recovered_median, col = simdate), size = 1.3) +
  geom_vline(xintercept = as.Date("2020-08-05"), linetype = "dashed", color = "grey") +
  theme(legend.position = "none") +
  labs(y = "Total recovered") +
  scale_y_continuous(labels = comma)




scen <- plot_grid(p1, p4, p5, p6,p3)
scen <- plot_grid(scen, legend, rel_widths = c(1, 0.3))


outdir <- file.path(project_path, paste0("NU_civis_outputs/", simdates[length(simdates)]))

fname <- paste0(scenario, "_comparison.png")
ggsave(fname, plot = scen, path = outdir, width = 20, height = 10, device = "png")
