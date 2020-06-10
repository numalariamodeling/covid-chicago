## ============================================================
## R script to get R(t) from Line list admission data used for fitting
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

dat <- dat %>%
  arrange(EMS, date) %>%
  group_by(EMS) %>%
  mutate(Date = as.Date(date), time = c(1:n_distinct(date)),
         EMS = factor(EMS, levels = c(1:11), labels = paste0("EMS_", c(1:11))))  %>%
  filter(Date >= as.Date("2020-01-01"))

ggplot(data = dat) +
  geom_bar(aes(x = Date, y = cases), stat = "identity") +
  facet_wrap(~EMS, scales = "free")

### Fill in missing dates ? 

method <- "uncertain_si"
Rt_list <- list()
si_list <- list()
for (region in unique(dat$EMS)) {
  # region = unique(dat$EMS)[1]
  disease_incidence_data <- dat %>%
    filter(EMS == region) %>%
    rename(I = cases)

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

  ## estimate the reproduction number (method "uncertain_si")
  
  ## biweekly sliding
  t_start <- seq(2, nrow(disease_incidence_data)-13)   
  t_end <- t_start + 13  
  
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



  ggsave(paste0(region, "_EpiEstim_default_", method, ".pdf"),
    plot = pplot3, path = file.path(getwd()), width = 6, height = 10, dpi = 300, device = "pdf"
  )


  Rt_list[[region]] <- res$R %>% mutate(region = region)
  
  #t_start_date = disease_incidence_data[t_start,"date"]
  
}


Rt_dat <- Rt_list %>% bind_rows()
Rt_dat$EMS <- factor(Rt_dat$region, levels = paste0("EMS_", c(1:11)), labels = paste0("EMS_", c(1:11)))


### Write csv file with Rt 
Rt_dat %>%
  merge(unique(dat[, c("time", "date")]), by.x = "t_start", by.y = "time") %>%
  rename(Date = date,
    geography_modeled = region,
    Median.of.covid.19.Rt = `Median(R)`,
    Lower.error.bound.of.covid.19.Rt = `Quantile.0.025(R)`,
    Upper.error.bound.of.covid.19.Rt = `Quantile.0.975(R)`
  ) %>%
  arrange(Date, geography_modeled) %>%
  select(Date, geography_modeled, Median.of.covid.19.Rt, Lower.error.bound.of.covid.19.Rt, Upper.error.bound.of.covid.19.Rt) %>%
  write.csv("nu_il_fromdata_estimated_Rt.csv", row.names = FALSE)


### Generate plots 
p_Rt <- ggplot(data = Rt_dat) +
  theme_bw() +
  geom_line(aes(x = t_start, y = `Median(R)`), col = "deepskyblue4", size = 1.3) +
  geom_ribbon(aes(x = t_start, ymin = `Quantile.0.025(R)`, ymax = `Quantile.0.975(R)`), fill = "deepskyblue4", alpha = 0.5) +
  facet_wrap(~EMS, scales = "free_y") +
  geom_hline(yintercept = 1, linetype = "dashed")


ggsave(paste0("Rt_data_uncertain_si_v1.pdf"),
       plot = p_Rt, width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_data_uncertain_si_v1.png"),
       plot = p_Rt, width = 14, height = 8, dpi = 300, device = "png"
) 

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

ggsave(paste0("Rt_data_uncertain_si_v2.pdf"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0("Rt_data_uncertain_si_v2.png"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "png"
)
