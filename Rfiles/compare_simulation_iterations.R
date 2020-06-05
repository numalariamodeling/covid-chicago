##==============================================================
## R script to plot the weekly deliverables together in one plot
##==============================================================


require(tidyverse)
require(cowplot)


source("load_paths.R")
source("processing_helpers.R")


simdates <- c("20200521", "20200526" , "20200603")
scenario <- "baseline" # june1partial10  , june1partial30

dat1 <- read.csv(file.path(project_path, paste0("NU_civis_outputs/", simdates[1], "/csv/nu_il_", scenario, "_", simdates[1], ".csv")))
dat2 <- read.csv(file.path(project_path, paste0("NU_civis_outputs/", simdates[2], "/csv/nu_il_", scenario, "_", simdates[2], ".csv")))
dat3 <- read.csv(file.path(project_path, paste0("NU_civis_outputs/", simdates[3], "/csv/nu_il_", scenario, "_", simdates[3], ".csv")))


dat1$simdate <- simdates[1]
dat2$simdate <- simdates[2]
dat3$simdate <- simdates[3]

dat <- dat3 %>%
  dplyr::select(colnames(dat1)) %>%
  rbind(dat1, dat2) %>%
  dplyr::mutate(Date=  as.Date(Date)) %>%
  filter(
    Date <= "2021-03-01",
    geography_modeled == "illinois"
  )


legend <- get_legend(ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.covid.19.infections,
    ymax = Upper.error.bound.of.covid.19.infections, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.Covid.19.infections, col = simdate), size = 1.3))


p1 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.covid.19.infections,
    ymax = Upper.error.bound.of.covid.19.infections, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.Covid.19.infections, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "Covid.19.infections")


p2 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.number.of.ventilators.used,
    ymax = Upper.error.bound.of.number.of.ventilators.used, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.ventilators.used, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "ventilators.used")


p3 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.covid.19.deaths,
    ymax = Upper.error.bound.of.covid.19.deaths, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.covid.19.deaths, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "covid.19.deaths")


p4 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.number.of.hospital.beds.occupied,
    ymax = Upper.error.bound.of.number.of.hospital.beds.occupied, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.hospital.beds.occupied, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "hospital.beds.occupied")


p5 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.number.of.ICU.beds.occupied,
    ymax = Upper.error.bound.of.number.of.ICU.beds.occupied, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.ICU.beds.occupied, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "ICU.beds.occupied")


p6 <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.on.recovered,
    ymax = Upper.error.bound.on.recovered, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Total.recovered, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "Total.recovered")


p5b <- ggplot(data = dat) +
  theme_cowplot() +
  geom_ribbon(aes(
    x = Date, ymin = Lower.error.bound.of.number.of.ICU.beds.occupied * 0.66,
    ymax = Upper.error.bound.of.number.of.ICU.beds.occupied * 0.66, fill = simdate
  ), alpha = 0.3) +
  geom_line(aes(x = Date, y = Number.of.ICU.beds.occupied * 0.66, col = simdate), size = 1.3) +
  theme(legend.position = "none") +
  labs(y = "ventilators.used_0.66")



scen <- plot_grid(p5, p2, p6, p5b)
scen <- plot_grid(scen, legend, rel_widths = c(1, 0.3))


outdir <- file.path(project_path, paste0("NU_civis_outputs/", simdates[length(simdates)]))

fname <- paste0(scenario, "_comparison.png")
ggsave(fname, plot = scen, path = outdir, width = 16, height = 10, device = "png")



