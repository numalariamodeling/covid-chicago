## ============================================================
## R script to get R(t) from simulation outputs from NU campus model
## Runs Rt estimation script for "Ki_NU" per "NUgrp", if other
## parameters vary, the for loop will need to be adjusted
## Input: trajectoriesDat.csv
## Output: combined_estimated_Rt.Rdata and combined_estimated_Rt.csv in 'estimatedRt' subfolder
## ============================================================

# install.packages("devtools")
# library(devtools)
# install_github("annecori/EpiEstim", force = TRUE)
library(tidyverse)
library(EpiEstim)
library(data.table)

# setwd() # setwd to Rfiles directory, or start from Rproject
source("load_paths.R")
source("processing_helpers.R")
source("estimate_Rt/getRt_function.R")

exp_name <- "20201001_NU_RR_NU_low_effective_0"
exp_dir <- file.path(simulation_output, exp_name)
Rt_dir <- file.path(exp_dir, "estimatedRt")
if (!dir.exists(Rt_dir)) dir.create(Rt_dir)


### Load simulation outputs
keepVars <- c("time", "startdate", "Ki_NU", "scen_num", "infected", "infected_campus", "infected_evanston", "infected_unofficial")
dat <- fread(file.path(exp_dir, "trajectoriesDat.csv"), select = keepVars) %>%
  dplyr::mutate(
    startdate = as.Date(startdate),
    Date = as.Date(time + startdate)
  ) %>%
  rename(infected_all = infected) %>%
  pivot_longer(cols = -c("time", "startdate", "Ki_NU", "Date", "scen_num")) %>%
  separate(name, into = c("outcome", "NUgrp")) %>%
  rename(infected = value) %>%
  dplyr::group_by(scen_num, Ki_NU, NUgrp) %>%
  dplyr::arrange(scen_num, Ki_NU, NUgrp, Date) %>%
  dplyr::mutate(infected_cumul = cumsum(infected)) %>%
  dplyr::mutate(new_infections = infected_cumul - lag(infected_cumul))


#### Calculate Rt for median predictions only, to be faster
#### Uncertainity estimates based on Rt estimation method
dat <- dat %>%
  dplyr::group_by(Date, startdate, Ki_NU, NUgrp) %>%
  dplyr::summarize(
    new_infections = median(new_infections, na.rm = TRUE),
    infected_cumul = median(infected_cumul, na.rm = TRUE)
  ) %>%
  mutate(scen_num = "aggregated_median") %>%
  ungroup() %>%
  as.data.frame()


savePlot <- TRUE
for (i in unique(dat$NUgrp)) {
  print(paste0("start NUgrp", i))
  # i= unique(dat$NUgrp)[1]

  method <- "uncertain_si"
  weekwindow <- 13

  Rt_list <- list()
  si_list <- list()
  count <- 0
  for (j in unique(dat$Ki_NU)) {
    print(paste0("start Ki_NU", j))
    count <- count + 1
    disease_incidence_data <- dat %>%
      dplyr::filter(NUgrp == i) %>%
      dplyr::filter(Ki_NU == j) %>%
      dplyr::rename(I = new_infections) %>%
      dplyr::mutate(I = ifelse(I < 0, 0, I)) %>%
      dplyr::select(Date, startdate, I, infected_cumul) %>%
      dplyr::filter(!is.na(I))

    res <- getRt(disease_incidence_data, method = method, weekwindow = weekwindow)

    if (savePlot) {
      pplot <- plot(res)
      ggsave(paste0(i, "_", j, "_EpiEstim_default_", method, ".pdf"),
        plot = pplot, path = file.path(Rt_dir), width = 6, height = 10, dpi = 300, device = "pdf"
      )
    }

    Rt_tempdat <- res$R %>% mutate(weekwindow = weekwindow)

    Rt_tempdat <- Rt_tempdat %>%
      rename(
        rt_mean = `Mean(R)`,
        rt_std = `Std(R)`,
        rt_q2.5 = `Quantile.0.025(R)`,
        rt_q5 = `Quantile.0.05(R)`,
        rt_q25 = `Quantile.0.25(R)`,
        rt_median = `Median(R)`,
        rt_q75 = `Quantile.0.75(R)`,
        rt_q95 = `Quantile.0.95(R)`,
        rt_q97.5 = `Quantile.0.975(R)`
      )

    Rt_tempdat$Ki_NU <- j
    Rt_tempdat$NUgrp <- i
    Rt_tempdat$date <- Rt_tempdat$t_end + unique(disease_incidence_data$startdate)

    if (count == 1) Rt_tempdat_All <- Rt_tempdat
    if (count != 1) Rt_tempdat_All <- rbind(Rt_tempdat_All, Rt_tempdat)

    SI_tempdat <- res$SI.Moments %>% mutate(weekwindow = weekwindow)
    SI_tempdat$Ki_NU <- j
    SI_tempdat$NUgrp <- i

    if (count == 1) SI_tempdat_All <- SI_tempdat
    if (count != 1) SI_tempdat_All <- rbind(SI_tempdat_All, SI_tempdat)

    rm(Rt_tempdat, SI_tempdat)
  }

  save(Rt_tempdat_All, file = file.path(Rt_dir, paste0(i, "_estimated_Rt.Rdata")))
}


#### Combine
datlist <- list()
rtfiles <- list.files(Rt_dir, pattern = "Rdata")
rtfiles <- rtfiles[!grepl("combined", rtfiles)]
for (rtfile in rtfiles) {
  load(file.path(file.path(Rt_dir, rtfile)))
  datlist[[length(datlist) + 1]] <- Rt_tempdat_All
}

Rtdat <- datlist %>% bind_rows()
save(Rtdat, file = file.path(Rt_dir, paste0("combined_estimated_Rt.Rdata")))
fwrite(Rtdat, file = file.path(Rt_dir, paste0("combined_estimated_Rt.csv")), quote = FALSE)
