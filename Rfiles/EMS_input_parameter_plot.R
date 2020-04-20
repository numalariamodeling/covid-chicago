require(tidyverse)
require(cowplot)
require(scales)

user_name <- Sys.getenv("USERNAME")

if (user_name == "mrung") {
  gitdir <- file.path("C:/Users/", user_name, "/gitrepos/covid-chicago/")
  projectdir <- file.path("C:/Users/", user_name, "/Box/NU-malaria-team/projects/covid_chicago/cms_sim/")
}


source(file.path(gitdir, "Rfiles/f_AggrDat.R"))

dat <- read_csv(file.path(projectdir, "simulation_output/_csv/EMS_trajectories_baseline_20200419.csv"))

### Aggregate for all EMS
datAggr <- dat %>%
  select(-run_num, -sample_num, -scen_num, -first_day) %>%
  dplyr::group_by() %>%
  dplyr::summarise_all(.funs = "mean")

### Aggregate per EMS and get distribution statistics
dat1 <- dat %>%
  select(-run_num, -sample_num, -scen_num, -first_day) %>%
  dplyr::group_by(time, date, ems) %>%
  f_aggrDat(groupVars = c("ems"), value = "social_multiplier_1", WideToLong = F) %>%
  mutate(var = "social_multiplier_1")

dat2 <- dat %>%
  select(-run_num, -sample_num, -scen_num, -first_day) %>%
  dplyr::group_by(time, date, ems) %>%
  f_aggrDat(groupVars = c("ems"), value = "social_multiplier_2", WideToLong = F) %>%
  mutate(var = "social_multiplier_2")

dat3 <- dat %>%
  select(-run_num, -sample_num, -scen_num, -first_day) %>%
  dplyr::group_by(time, date, ems) %>%
  f_aggrDat(groupVars = c("ems"), value = "social_multiplier_3", WideToLong = F) %>%
  mutate(var = "social_multiplier_3")


datKi <- dat %>%
  select(-run_num, -sample_num, -scen_num, -first_day) %>%
  dplyr::group_by(time, date, ems) %>%
  f_aggrDat(groupVars = c("ems"), value = "Ki", WideToLong = F) %>%
  mutate(var = "Ki")

datCFR <- dat %>%
  select(-run_num, -sample_num, -scen_num, -first_day) %>%
  dplyr::group_by(time, date, ems) %>%
  f_aggrDat(groupVars = c("ems"), value = "cfr", WideToLong = F) %>%
  mutate(var = "cfr")

#### Combine dataframe for plotting
datSIP <- as.data.frame(rbind(dat1, dat2, dat3, datKi, datCFR))
sip <- datSIP %>%
  filter(var == "social_multiplier_1") %>%
  dplyr::select(ems, mean.val) %>%
  arrange(mean.val) %>%
  select(ems)
sip <- sip$ems
datSIP$ems_sip <- factor(datSIP$ems, levels = c(1:11), labels = sip)

p1 <- ggplot(subset(datSIP, var != "Ki" & var != "cfr")) + theme_cowplot() +
  geom_pointrange(aes(x = reorder(ems, mean.val), y = mean.val, ymin = min.val, ymax = max.val, col = var), size = 1) +
  labs(title = "SIP", x = "", y = "", col = "") +
  geom_hline(yintercept = mean(datAggr$social_multiplier_1), col = "#a1dab4", size = 1) +
  geom_hline(yintercept = mean(datAggr$social_multiplier_2), col = "#41b6c4", size = 1) +
  geom_hline(yintercept = mean(datAggr$social_multiplier_3), col = "#225ea8", size = 1) +
  geom_hline(yintercept = (datAggr$social_multiplier_3 + datAggr$social_multiplier_1 + datAggr$social_multiplier_2) / 3, col = "black", linetype = "dashed", size = 1) +
  scale_color_manual(values = (c("#a1dab4", "#41b6c4", "#225ea8"))) +
  theme(legend.position = "top")

p1b <- ggplot(subset(datSIP, var == "Ki")) + theme_cowplot() +
  geom_pointrange(aes(x = ems_sip, y = mean.val, ymin = min.val, ymax = max.val, col = var), size = 1) +
  labs(title = "Transmission rate (Ki)", x = "", y = "", col = "") +
  geom_hline(yintercept = mean(datAggr$Ki), col = "deepskyblue2", size = 1) +
  scale_color_manual(values = (c("deepskyblue2"))) +
  theme(legend.position = "none")


p1c <- ggplot(subset(datSIP, var == "cfr")) + theme_cowplot() +
  geom_pointrange(aes(x = ems_sip, y = mean.val, ymin = min.val, ymax = max.val, col = var), size = 1) +
  labs(title = "CFR", x = "EMS ordered by SIP effect size", y = "", col = "") +
  geom_hline(yintercept = mean(datAggr$cfr), col = "darkorange2", size = 1) +
  scale_color_manual(values = (c("darkorange2"))) +
  theme(legend.position = "none")


p2 <- ggplot(subset(datSIP, var == "Ki")) + theme_cowplot() +
  geom_pointrange(aes(x = reorder(ems, mean.val), y = mean.val, ymin = min.val, ymax = max.val, col = var), size = 1) +
  labs(x = "EMS ordered by SIP effect size", y = "SIP effect size", col = "") +
  geom_hline(yintercept = mean(datAggr$Ki), col = "deepskyblue2", size = 1) +
  scale_color_manual(values = (c("deepskyblue2")))


p3 <- ggplot(subset(datSIP, var == "cfr")) + theme_cowplot() +
  geom_pointrange(aes(x = reorder(ems, mean.val), y = mean.val, ymin = min.val, ymax = max.val, col = var), size = 1) +
  labs(x = "EMS ordered by SIP effect size", y = "SIP effect size", col = "") +
  geom_hline(yintercept = mean(datAggr$cfr), col = "darkorange2", size = 1) +
  scale_color_manual(values = (c("darkorange2")))


#### Combine plots
pout <- plot_grid(p1, p1b, p1c, ncol = 1, rel_heights = c(1, 0.5, 0.5))

ggsave(file.path(projectdir, "inputs/_plots", "20200419_fitted_param.png"), pout, width = 10, height = 8)
