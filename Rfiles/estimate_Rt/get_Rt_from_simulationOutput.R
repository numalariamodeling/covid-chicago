## ============================================================
## R script to get R(t) from simulation outputs
## ============================================================

# install.packages("devtools")
# library(devtools)
# install_github("annecori/EpiEstim", force = TRUE)

library(tidyverse)
library(EpiEstim)


source("load_paths.R")
source("processing_helpers.R")
setwd("estimate_Rt/from_simulations")

### Load simulation outputs
dat <- read.csv(file.path(project_path, "NU_civis_outputs/20200603/csv/nu_il_baseline_20200603.csv"))
summary(as.Date(dat$Date))


Rt_non_parametric_si_list <- list()
Rt_parametric_si_list <- list()
Rt_uncertain_si_list <- list()

for (region in unique(dat$geography_modeled)) {
  # region = unique(dat$geography_modeled)[1]
  disease_incidence_data <- dat %>%
    filter(geography_modeled == region) %>%
    select(Number.of.Covid.19.new.infections) %>%
    rename(I = Number.of.Covid.19.new.infections)

  # write.csv(disease_incidence_data,paste0(region,"disease_incidence_data.csv") , row.names = FALSE)


  ## check what si_distr to assume, or calculate from predictions, here using an example from the package
  # si_distr <- c(0.000, 0.233, 0.359, 0.198, 0.103, 0.053, 0.027 ,0.014 ,0.007, 0.003, 0.002 ,0.001)
  # res_non_parametric_si <- estimate_R(incid = disease_incidence_data$I,
  #                  method = "non_parametric_si",
  #                  config = make_config(list(si_distr = si_distr)))
  #
  # res_parametric_si <- estimate_R(incid = disease_incidence_data$I,
  #                               method = "parametric_si",
  #                                config = make_config(list(mean_si = 2.6, std_si = 1.5)))
  ## estimate the reproduction number (method "uncertain_si")
  
  ### Use uncertain_si
  method = "uncertain_si"
  res <- estimate_R(disease_incidence_data$I,
    method = "uncertain_si",
    config = make_config(list(
      mean_si = 2.6, std_mean_si = 1,
      min_mean_si = 1, max_mean_si = 4.2,
      std_si = 1.5, std_std_si = 0.5,
      min_std_si = 0.5, max_std_si = 2.5,
      n1 = 100, n2 = 100
    ))
  )

  pplot <- plot(res_uncertain_si)

  ggsave(paste0(region, "_EpiEstim_default_",method,".pdf"),
    plot = pplot, path = file.path(getwd()), width = 6, height = 10, dpi = 300, device = "pdf"
  )

  Rt_list[[region]] <- res$R %>% mutate(region = region)
  si_list[[region]] <- res$SI.Moments %>% mutate(region = region)
}


Rt_dat <- Rt_list %>% bind_rows()
table(Rt_dat$region)


Rt_dat %>%
  merge(unique(dat[, c("time", "Date")]), by.x = "t_start", by.y = "time") %>%
  rename(
    geography_modeled = region,
    Median.of.covid.19.Rt = `Median(R)`,
    Lower.error.bound.of.covid.19.Rt = `Quantile.0.025(R)`,
    Upper.error.bound.of.covid.19.Rt = `Quantile.0.975(R)`
  ) %>%
  arrange(Date, geography_modeled) %>%
  select(Date, geography_modeled, Median.of.covid.19.Rt, Lower.error.bound.of.covid.19.Rt, Upper.error.bound.of.covid.19.Rt) %>%
  write.csv("nu_il_baseline_estimated_Rt.csv", row.names = FALSE)

Rt_dat <- Rt_dat %>% filter(region %in% paste0("ems", c(1:11)))
Rt_dat$EMS <- factor(Rt_dat$region, levels = paste0("ems", c(1:11)), labels = paste0("EMS_", c(1:11)))


dat <- dat %>%
  filter(geography_modeled %in% paste0("ems", c(1:11))) %>%
  rename(region = geography_modeled)

dat$EMS <- factor(dat$region, levels = paste0("ems", c(1:11)), labels = paste0("EMS_", c(1:11)))


dat <- dat %>%
  arrange(EMS, Date) %>%
  group_by(EMS) %>%
  mutate(date = as.Date(Date), time = c(1:n_distinct(date)))

tapply(dat$time, dat$EMS, summary)



pall <- ggplot(data = subset(Rt_dat, t_start <= 210)) +
  theme_bw() +
  geom_line(aes(x = t_start, y = `Median(R)`), col = "deepskyblue3", size = 1.3) +
  geom_ribbon(aes(x = t_start, ymin = `Quantile.0.025(R)`, ymax = `Quantile.0.975(R)`), fill = "deepskyblue3", alpha = 0.5) +
  facet_wrap(~EMS, scales = "free_y") +
  geom_hline(yintercept = 1, linetype = "dashed") +
  customThemeNoFacet


pcut <- ggplot(data = subset(Rt_dat, t_start <= 210)) +
  theme_bw() +
  geom_line(aes(x = t_start, y = `Median(R)`), col = "deepskyblue3", size = 1.3) +
  geom_ribbon(aes(x = t_start, ymin = `Quantile.0.025(R)`, ymax = `Quantile.0.975(R)`), fill = "deepskyblue3", alpha = 0.5) +
  facet_wrap(~EMS, scales = "free_y") +
  geom_hline(yintercept = 1, linetype = "dashed") +
  customThemeNoFacet


summary(dat[dat$Date <= "2020-10-01", "time"])
summary(dat$time)
summary(Rt_uncertain_si_dat$t_start)


scl <- mean(dat$Number.of.Covid.19.new.infections) / mean(Rt_dat$`Median(R)`)

pplot <- ggplot(data = subset(Rt_dat, t_start <= 210)) +
  theme_bw() +
  geom_bar(data = subset(dat, time <= 210), aes(x = time, y = Number.of.Covid.19.new.infections / scl), fill = "grey", stat = "identity", alpha = 0.9) +
  geom_line(aes(x = t_start, y = `Median(R)`), col = "deepskyblue4", size = 1.3) +
  geom_ribbon(aes(x = t_start, ymin = `Quantile.0.025(R)`, ymax = `Quantile.0.975(R)`), fill = "deepskyblue4", alpha = 0.5) +
  facet_wrap(~EMS, scales = "free_y") +
  geom_hline(yintercept = 1, linetype = "dashed") +
  scale_y_continuous("R0", sec.axis = sec_axis(~ . * scl, name = "Cases")) +
  labs(caption = "Using 'uncertain_si' distribution") +
  customThemeNoFacet


ggsave(paste0("Rt_simulation_uncertain_si_v3.pdf"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_simulation_uncertain_si_v3.png"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "png"
)
ggsave(paste0("Rt_simulation_uncertain_si_v2.pdf"),
  plot = pcut, width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_simulation_uncertain_si_v2.png"),
  plot = pcut, width = 14, height = 8, dpi = 300, device = "png"
)

ggsave(paste0("Rt_simulation_uncertain_si_v1.png"),
  plot = pall, width = 14, height = 8, dpi = 300, device = "png"
)
