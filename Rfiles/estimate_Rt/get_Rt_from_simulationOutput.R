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
outdir <- file..path("estimate_Rt/from_simulations")

### Load simulation outputs
dat <- read.csv(file.path(project_path, "NU_civis_outputs/20200603/csv/nu_il_baseline_20200603.csv"))
summary(as.Date(dat$Date))

dat <- dat %>%
  filter(geography_modeled %in% paste0("ems", c(1:11))) %>%
  rename(region = geography_modeled)

dat$EMS <- factor(dat$region,  levels = paste0("ems", c(1:11)), labels = paste0("EMS_", c(1:11)))


dat <- dat %>%
  arrange(EMS, Date) %>%
  group_by(EMS) %>%
  mutate(date = as.Date(Date), time = c(1:n_distinct(date)))


method <- "uncertain_si"
Rt_list <- list()
si_list <- list()

for (region in unique(dat$geography_modeled)) {
  # region = unique(dat$geography_modeled)[1]
  disease_incidence_data <- dat %>%
    filter(geography_modeled == region) %>%
    select(Number.of.Covid.19.new.infections) %>%
    rename(I = Number.of.Covid.19.new.infections)

  ## check what si_distr to assume, or calculate from predictions, here using an example from the package
  if(method=="non_parametric_si"){  
    si_distr <- c(0.000, 0.233, 0.359, 0.198, 0.103, 0.053, 0.027 ,0.014 ,0.007, 0.003, 0.002 ,0.001)
    res <- estimate_R(incid = disease_incidence_data$I,
                      method = "non_parametric_si",
                      config = make_config(list(si_distr = si_distr)))
    
  }
  
  ### use parametric_si
  if(method=="parametric_si"){  
    res <- estimate_R(incid = disease_incidence_data$I,
                      method = "parametric_si",
                      config = make_config(list(mean_si = 2.6, std_si = 1.5)))
  }
  
  ## biweekly sliding
  t_start <- seq(2, nrow(disease_incidence_data)-13)   
  t_end <- t_start + 13  
  
  ## estimate the reproduction number (method "uncertain_si")
  if(method=="uncertain_si"){
    res <- estimate_R(disease_incidence_data$I,
                      method = "uncertain_si",
                      config = make_config(list(
                        t_start = t_start, 
                        t_end = t_end,
                        mean_si = 4.6, std_mean_si = 1,
                        min_mean_si = 1, max_mean_si = 7.5,
                        std_si = 1.5, std_std_si = 0.5,
                        min_std_si = 0.5, max_std_si = 2.5,
                        n1 = 100, n2 = 100
                      ))
    )
  }

  pplot <- plot(res)

  ggsave(paste0(region, "_EpiEstim_default_",method,".pdf"),
    plot = pplot, path = file.path(outdir), width = 6, height = 10, dpi = 300, device = "pdf"
  )

  Rt_list[[region]] <- res$R %>% mutate(region = region)
  si_list[[region]] <- res$SI.Moments %>% mutate(region = region)
}


### Combine list to dataframe 
Rt_dat <- Rt_list %>% bind_rows()
table(Rt_dat$region)


### Write csv file with Rt 
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



#### Edit dataframe
Rt_dat <- Rt_dat %>% filter(region %in% paste0("ems", c(1:11))) %>%
  mutate(EMS = factor(region, levels = paste0("ems", c(1:11)), labels = paste0("EMS_", c(1:11))))


## Used for secondary axis in plot showing both cases and Rt
scl <- mean(dat$Number.of.Covid.19.new.infections) / mean(Rt_dat$`Median(R)`)



### Generate plots 
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
  plot = pplot, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_simulation_uncertain_si_v3.png"),
  plot = pplot, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "png"
)
ggsave(paste0("Rt_simulation_uncertain_si_v2.pdf"),
  plot = pcut, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_simulation_uncertain_si_v2.png"),
  plot = pcut, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "png"
)

ggsave(paste0("Rt_simulation_uncertain_si_v1.png"),
  plot = pall, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "png"
)
