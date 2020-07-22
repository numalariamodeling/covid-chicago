### ------------------------------------------------------------------------
#### R scriot to plot the time varying Ki parameter per EMS
### -----------------------------------------------------------------------

library(viridis)
library(tidyverse)
library(cowplot)

source("load_paths.R")

### Options for plot theme
customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 12, face = "bold"),
  strip.text.y = element_text(size = 12, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 16, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 12),
  plot.caption = element_text(size = 8),
  legend.title = element_text(size = 12),
  legend.text = element_text(size = 12),
  axis.title.x = element_text(size = 12),
  axis.text.x = element_text(size = 12),
  axis.title.y = element_text(size = 12),
  axis.text.y = element_text(size = 12)
)


### Load trajectories Dat
exp_name <- "20200630_IL_1_endsip35"
Ki_dat <- read.csv(file.path(simulation_output, exp_name, "trajectoriesDat.csv"))
# Ki_dat <- read.csv(file.path(project_path, "NU_civis_outputs", "20200624", "trajectories", "trajectoriesDat_baseline.csv"))


### Note use Ki_EMS-  or Ki_EMS.   not Ki_EMS_  (time varying vs input parameter)
colnames(Ki_dat) <- gsub("[.]", "-", colnames(Ki_dat))
Kivars <- paste0("Ki_EMS-", c(1:11))
keepvars <- c("time", "startdate", Kivars)

### Wide to long format and calculate date
### Aand aggregate samples
Ki_dat <- Ki_dat %>%
  select(keepvars) %>%
  mutate(date = as.Date(startdate) + time) %>%
  pivot_longer(cols = -c("time", "date", "startdate"), names_to = "region") %>%
  mutate(
    region = gsub("EMS-", "", gsub("Ki_", "", region)),
    region = as.numeric(region)
  ) %>%
  group_by(date, region) %>%
  summarize(value = mean(value))

### Plot
pplot <- ggplot(data = subset(Ki_dat, date <= as.Date("2020-08-01"))) +
  theme_cowplot() +
  geom_line(aes(x = date, y = value, col = as.factor(region), group = region), size = 1.3) +
  scale_color_viridis(discrete = TRUE) +
  labs(color = "EMS", y = "Transmission rate") +
  customThemeNoFacet +
  labs(x = "")

ggsave(paste0("Ki_timeline.png"),
  plot = pplot, path = file.path(simulation_output), width = 10, height = 5, device = "png"
)

ggsave(paste0("Ki_timeline.pdf"),
  plot = pplot, path = file.path(simulation_output), width = 10, height = 5, device = "pdf"
)



##### Plot Ki and hospital admissions
plotKi_and_admissions <- FALSE
if (plotKi_and_admissions) {
  dat <- read.csv(file.path(data_path, "covid_IDPH/Cleaned Data/200701_jg_admission_date_ems.csv"))
  dat <- dat %>%
    rename(region = EMS) %>%
    mutate(date = as.Date(date)) %>%
    merge(Ki_dat, by = c("date", "region"), all = TRUE)
  dat_long <- dat %>% pivot_longer(cols = -c("date", "region"))

  p1 <- ggplot(data = subset(dat, date > as.Date("2020-03-01") & date <= as.Date("2020-06-01"))) +
    theme_cowplot() +
    geom_line(aes(x = date, y = value, col = as.factor(region), group = region), size = 1.3) +
    # scale_color_viridis(discrete = TRUE) +
    scale_color_manual(values = c(
      "darkorchid2", "deepskyblue2", "mediumpurple3", "orchid1", "orange2",
      "olivedrab3", "goldenrod1", "cornflowerblue", "cadetblue1", "coral1", "chartreuse4"
    )) +
    labs(color = "EMS", y = "Transmission rate") +
    customThemeNoFacet +
    labs(x = "")


  p2 <- ggplot(data = subset(dat, date > as.Date("2020-03-01") & date <= as.Date("2020-06-01"))) +
    theme_cowplot() +
    geom_smooth(aes(x = date, y = cases, col = as.factor(region), group = region), size = 1.3, se = FALSE, span = 0.5) +
    # scale_color_viridis(discrete = TRUE) +
    scale_color_manual(values = c(
      "darkorchid2", "deepskyblue2", "mediumpurple3", "orchid1", "orange2",
      "olivedrab3", "goldenrod1", "cornflowerblue", "cadetblue1", "coral1", "chartreuse4"
    )) +
    labs(color = "EMS", y = "Hospital admissions") +
    customThemeNoFacet +
    labs(x = "") +
    scale_y_log10()

  pplot <- plot_grid(p1, p2)
  ggsave(paste0("Ki_cases_timeline.pdf"),
    plot = pplot, path = file.path(simulation_output), width = 10, height = 5, device = "pdf"
  )
}
