library(tidyverse)
library(cowplot)

dat <- read.csv("C:/Users/mrung/gitrepos/covid-chicago/trajectoriesDat.csv")

customTheme <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.text.y = element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 14),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 16),
  axis.title.y = element_text(size = 16),
  axis.text.x = element_text(size = 16),
  axis.text.y = element_text(size = 16)
)
cols <- c("FullFactorial" = "grey", "Ki" = "mediumvioletred", "initial_infect" = "deepskyblue3",
          "incubation_pd" = "tan2", "recovery_rate" = "olivedrab4")

unique(plotdat$Ki)
unique(plotdat$initial_infect)
unique(plotdat$incubation_pd)
unique(plotdat$recovery_rate)

plotdat <- dat %>%
  filter(time <= 30) %>%
  select(-X, -params) %>%
  pivot_longer(cols = c(susceptible, exposed, infectious, recovered), names_to = "outcome")
# pivot_longer(cols=c(initial_infect ,   Ki, incubation_pd, recovery_rate), names_to = "param_name", values_to="param_val")

plotdat$outcome <- factor(plotdat$outcome,
  levels = c("susceptible", "exposed", "infectious", "recovered"),
  labels = c("susceptible", "exposed", "infectious", "recovered")
)

p1 <- ggplot() + theme_cowplot() +
  geom_line(
    data = subset(plotdat),
    aes(x = time, y = value, group = scen_num, col = "FullFactorial"), size = 0.7, alpha = 0.7
  ) +
  geom_line(
    data = subset(plotdat, Ki == 0.312 & incubation_pd == 6.63 & recovery_rate == 6),
    aes(x = time, y = value, group = scen_num, col = "initial_infect"), size = 1.3
  ) +
  geom_line(
    data = subset(plotdat, initial_infect == 5 & incubation_pd == 6.63 & recovery_rate == 6),
    aes(x = time, y = value, group = scen_num, col = "Ki"), size = 1.3
  ) +
  geom_line(
    data = subset(plotdat, initial_infect == 5 & Ki == 0.312 & recovery_rate == 6),
    aes(x = time, y = value, group = scen_num, col = "incubation_pd"), size = 1.3
  ) +
  geom_line(
    data = subset(plotdat, initial_infect == 5 & Ki == 0.312 & incubation_pd == 6.63),
    aes(x = time, y = value, group = scen_num, col = "recovery_rate"), size = 1.3
  ) +
  scale_color_manual(values = cols) +
  labs(subtitle="Explorative plot SEIR model (cms) trajectories",
    x = "Time [days]", y = "Population [N]", color = "Parameter",
    caption = "\nBase parameter: initial_infect=5 (1,5,10), Ki=0.312 (0.0009, 0.050,0.312) & \nincubation_pd=6.63 (4.20,6.63,12.40) & recovery_rate=6 (6, 13,16) "
  ) +
  facet_wrap(~outcome, scales = "free") +
  customTheme



##### Hospitaliszations and deaths (from python script, to do: add sample num)
CFR <- 0.016
fraction_symptomatic <- 0.7
fraction_hospitalized <- 0.3
fraction_critical <- 0.8
time_to_hospitalization <- 6
time_to_critical <- 6
time_to_death <- 2

fraction_death <- CFR / (fraction_hospitalized * fraction_critical)

dat["time_hospitalized"] <- dat["time"] + time_to_hospitalization
dat["time_critical"] <- dat["time_hospitalized"] + time_to_critical
dat["time_death"] <- dat["time_critical"] + time_to_death

dat["symptomatic"] <- dat["infectious"] * fraction_symptomatic
dat["hospitalized"] <- dat["symptomatic"] * fraction_hospitalized
dat["critical"] <- dat["hospitalized"] * fraction_critical
dat["death"] <- dat["critical"] * fraction_death



plotdat <- dat %>%
  filter(time <= 30) %>%
  select(-X, -params) %>%
  pivot_longer(cols = c(symptomatic, hospitalized, critical, death), names_to = "outcome")
# pivot_longer(cols=c(initial_infect ,   Ki, incubation_pd, recovery_rate), names_to = "param_name", values_to="param_val")

p2 <- ggplot() + theme_cowplot() +
  geom_line(
    data = subset(plotdat),
    aes(x = time, y = value, group = scen_num, col = "FullFactorial"), size = 0.7, alpha = 0.7
  ) +
  geom_line(
    data = subset(plotdat, Ki == 0.312 & incubation_pd == 6.63 & recovery_rate == 6),
    aes(x = time, y = value, group = scen_num, col = "initial_infect"), size = 1.3
  ) +
  geom_line(
    data = subset(plotdat, initial_infect == 5 & incubation_pd == 6.63 & recovery_rate == 6),
    aes(x = time, y = value, group = scen_num, col = "Ki"), size = 1.3
  ) +
  geom_line(
    data = subset(plotdat, initial_infect == 5 & Ki == 0.312 & recovery_rate == 6),
    aes(x = time, y = value, group = scen_num, col = "incubation_pd"), size = 1.3
  ) +
  geom_line(
    data = subset(plotdat, initial_infect == 5 & Ki == 0.312 & incubation_pd == 6.63),
    aes(x = time, y = value, group = scen_num, col = "recovery_rate"), size = 1.3
  ) +
  scale_color_manual(values = cols) +
  labs(subtitle="Explorative plot SEIR model (cms) trajectories",
    x = "Time [days]", y = "Population [N]", color = "Parameter",
    caption = "\nBase parameter: initial_infect=5 (1,5,10), Ki=0.312 (0.0009, 0.050,0.312) & \nincubation_pd=6.63 (4.20,6.63,12.40) & recovery_rate=6 (6, 13,16) "
  ) +
  facet_wrap(~outcome, scales = "free") +
  customTheme


print(p1)
print(p2)
ggsave(paste0("cms_testfull_out1.png"),
  plot = p1, width = 10, height = 8, device = "png"
)

ggsave(paste0("cms_testfull_out2.png"),
  plot = p2, width = 10, height = 8, device = "png"
)
