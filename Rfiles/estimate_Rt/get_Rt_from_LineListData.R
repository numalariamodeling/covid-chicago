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
setwd("estimate_Rt/from_data")

### Load simulation outputs
dat <- read.csv(file.path(data_path, "covid_IDPH/Cleaned Data/200608_jg_admission_date_ems.csv"))
summary(as.Date(dat$date))

ggplot(data = dat) +
  geom_bar(aes(x = date, y = cases), stat = "identity") +
  facet_wrap(~EMS, scales = "free")


Rt_non_parametric_si_list <- list()
Rt_parametric_si_list <- list()
Rt_uncertain_si_list <- list()

for (region in unique(dat$EMS)) {
  # region = unique(dat$EMS)[1]
  disease_incidence_data <- dat %>%
    filter(EMS == region) %>%
    select(cases) %>%
    rename(I = cases)

  # write.csv(disease_incidence_data,paste0(region,"disease_incidence_data.csv") , row.names = FALSE)


  ## check what si_distr to assume, or calculate from predictions, here using an example from the package
  # si_distr <- c(0.000, 0.233, 0.359, 0.198, 0.103, 0.053, 0.027 ,0.014 ,0.007, 0.003, 0.002 ,0.001)
  # res <- estimate_R(incid = disease_incidence_data$I,
  #                                     method = "non_parametric_si",
  #                                     config = make_config(list(si_distr = si_distr)))
  #
  #### use parametric_si
  # res <- estimate_R(incid = disease_incidence_data$I,
  #                                 method = "parametric_si",
  #                                 config = make_config(list(mean_si = 2.6, std_si = 1.5)))


  ## estimate the reproduction number (method "uncertain_si")
  method <- "uncertain_si"
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

  pplot <- plot(res)



  ggsave(paste0(region, "_EpiEstim_default_", method, ".pdf"),
    plot = pplot3, path = file.path(getwd()), width = 6, height = 10, dpi = 300, device = "pdf"
  )


  Rt_list[[region]] <- res$R %>% mutate(region = region)
}


Rt_dat <- Rt_list %>% bind_rows()
Rt_dat$EMS <- factor(Rt_list$region, levels = c(1:11), labels = paste0("EMS_", c(1:11)))

ggplot(data = dat) +
  geom_bar(aes(x = date, y = cases), stat = "identity") +
  facet_wrap(~EMS, scales = "free")


dat <- dat %>%
  arrange(EMS, date) %>%
  group_by(EMS) %>%
  mutate(date = as.Date(date), time = c(1:n_distinct(date)))

tapply(dat$time, dat$EMS, summary)

dat$EMS <- factor(dat$EMS, levels = c(1:11), labels = paste0("EMS_", c(1:11)))


ggplot(data = Rt_dat) +
  theme_bw() +
  geom_line(aes(x = t_start, y = `Median(R)`), col = "deepskyblue3", size = 1.3) +
  geom_ribbon(aes(x = t_start, ymin = `Quantile.0.025(R)`, ymax = `Quantile.0.975(R)`), fill = "deepskyblue3", alpha = 0.5) +
  facet_wrap(~EMS, scales = "free_y") +
  geom_hline(yintercept = 1, linetype = "dashed")


summary(dat$time)
summary(Rt_dat$t_start)

pplot <- ggplot(data = Rt_dat) +
  theme_bw() +
  geom_bar(data = dat, aes(x = time, y = cases / 20.12886), fill = "grey", stat = "identity", alpha = 0.9) +
  geom_line(aes(x = t_start, y = `Median(R)`), col = "deepskyblue4", size = 1.3) +
  geom_ribbon(aes(x = t_start, ymin = `Quantile.0.025(R)`, ymax = `Quantile.0.975(R)`), fill = "deepskyblue4", alpha = 0.5) +
  facet_wrap(~EMS, scales = "free_y") +
  geom_hline(yintercept = 1, linetype = "dashed") +
  scale_y_continuous("R0", sec.axis = sec_axis(~ . * 20.12886, name = "Cases")) +
  labs(caption = "Using 'uncertain_si' distribution") +
  customThemeNoFacet

ggsave(paste0("Rt_data_uncertain_si.pdf"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_data_uncertain_si.png"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "png"
)
