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
source("estimate_Rt/getRt_function.R")

outdir <- file.path("estimate_Rt/from_simulations")

simdate = "20200729"
### Load simulation outputs
dat <- read.csv(file.path(project_path, "NU_civis_outputs",simdate,paste0("csv/nu_il_baseline_",simdate,".csv")))
summary(as.Date(dat$Date))

method <- "uncertain_si"
weekwindow=13
Rt_list <- list()
si_list <- list()

for (region in unique(dat$geography_modeled)) {
  # region = unique(dat$geography_modeled)[1]
  disease_incidence_data <- dat %>%
    filter(geography_modeled == region) %>%
    rename(I = Number.of.Covid.19.new.infections)

  res <- getRt(disease_incidence_data, method=method, weekwindow=weekwindow)

  pplot <- plot(res)
  ggsave(paste0(region, "_EpiEstim_default_",method,".pdf"),
    plot = pplot, path = file.path(outdir), width = 6, height = 10, dpi = 300, device = "pdf"
  )

  Rt_list[[region]] <- res$R %>% mutate(region = region, weekwindow=weekwindow )
  si_list[[region]] <- res$SI.Moments %>% mutate(region = region , weekwindow=weekwindow)
}

### Combine list to dataframe 
Rt_dat <- Rt_list %>% bind_rows()
table(Rt_dat$region)


dat <- dat %>%
  filter(geography_modeled %in% paste0("covidregion_", c(1:11))) %>%
  rename(region = geography_modeled)

dat$covidregion <- factor(dat$region,  levels = paste0("covidregion_", c(1:11)), labels = paste0("covidregion_", c(1:11)))

### Write csv file with Rt 
dat <- dat %>%
  arrange(covidregion, Date) %>%
  dplyr::group_by(covidregion) %>%
  mutate(date = as.Date(Date), time = c(1:n_distinct(date)))

Rt_dat %>%
  mutate(t_start=t_start+weekwindow, t_end = t_end+weekwindow) %>%
  merge(unique(dat[, c("time", "Date")]), by.x = "t_start", by.y = "time") %>%
  rename(geography_modeled = region,
    Median.of.covid.19.Rt = `Median(R)`,
    Lower.error.bound.of.covid.19.Rt = `Quantile.0.025(R)`,
    Upper.error.bound.of.covid.19.Rt = `Quantile.0.975(R)`
  ) %>%
  arrange(Date, geography_modeled) %>%
  filter(
    Date <= "2020-12-01") %>%
  dplyr::select(Date, geography_modeled, Median.of.covid.19.Rt, Lower.error.bound.of.covid.19.Rt, Upper.error.bound.of.covid.19.Rt) %>%
  write.csv(file.path(project_path, "NU_civis_outputs" ,simdate, paste0("estimate_Rt","/nu_il_baseline_estimated_Rt_",simdate,".csv"), row.names = FALSE)
