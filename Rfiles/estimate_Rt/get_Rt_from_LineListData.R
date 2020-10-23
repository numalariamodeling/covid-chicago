## ============================================================
## R script to get R(t) from Line list admission data used for fitting
## ============================================================

# install.packages("devtools")
# library(devtools)
# install_github("annecori/EpiEstim", force = TRUE)

library(tidyverse)
library(EpiEstim)

source("load_paths.R")
source("setup.R")
source("processing_helpers.R")
source("estimate_Rt/getRt_function.R")

outdir <- file.path(project_path,"Plots + Graphs/Rt_plots")
today <- gsub("-", "", Sys.Date())
data_date = "200917"

### Load simulation outputs
dat <- read.csv(file.path(data_path, "covid_IDPH/Cleaned Data/",data_date,"_jg_aggregated_covidregion.csv"))
summary(as.Date(dat$date))

dat <- dat %>%
  arrange(covid_region, date) %>%
  group_by(covid_region) %>%
  mutate(Date = as.Date(date), time = c(1:n_distinct(date))) %>%
  filter(Date >= as.Date("2020-01-01"))

ggplot(data = dat) +
  geom_bar(aes(x = Date, y = cases), stat = "identity") +
  facet_wrap(~covid_region, scales = "free")

### Fill in missing dates ?

method <- "uncertain_si"
weekwindow <- 13
Rt_list <- list()
si_list <- list()

for (region in unique(dat$covid_region)) {
  # region = unique(dat$covid_region)[1]
  disease_incidence_data <- dat %>%
    filter(covid_region == region) %>%
    rename(I = cases)

  res <- getRt(disease_incidence_data, method = method, weekwindow = weekwindow)

  pplot <- plot(res)

  SAVE_plot =FALSE
  if(SAVE_plot){
   ggsave(paste0(region, "_EpiEstim_default_", method, ".pdf"),
    plot = pplot, path = file.path(outdir), width = 6, height = 10, dpi = 300, device = "pdf"
   )
  }


  Rt_list[[region]] <- res$R %>% mutate(region = region)
}


Rt_dat <- Rt_list %>% bind_rows()

### Write csv file with Rt
Rt_dat <- Rt_dat %>%
  mutate(time = t_end) %>%
  rename(
    covid_region = region,
    rt_median = `Median(R)`,
    rt_lower = `Quantile.0.025(R)`,
    rt_upper = `Quantile.0.975(R)`
  ) %>%
  merge(unique(dat[, c("time", "date", "covid_region")]), by = c("time", "covid_region")) %>%
  select(date, covid_region, rt_median, rt_lower, rt_upper)

Rt_dat$date <- as.Date(Rt_dat$date)
write.csv(Rt_dat, "nu_il_fromdata_estimated_Rt.csv", row.names = FALSE)


### Generate plots

p_Rt <- ggplot(data = Rt_dat) +
  theme_bw() +
  geom_line(aes(x = date, y = rt_median), col = "deepskyblue4", size = 1.3) +
  geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue4", alpha = 0.5) +
  facet_wrap(~covid_region, scales = "free") +
  geom_hline(yintercept = 1, linetype = "dashed") +
  labs(fill = "", color = "", x = "", y = expression(italic(R[t])), caption = "method = uncertain_si") +
  scale_x_date(breaks = "30 days", date_labels = "%d\n%b") +
  customThemeNoFacet


ggsave(paste0(today, "_Rt_estimated_from_data.pdf"),
  plot = p_Rt, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0(today, "_Rt_estimated_from_data.png"),
  plot = p_Rt, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "png"
)


p_Rt <- ggplot(data = subset(Rt_dat, date > as.Date("2020-08-01"))) +
  theme_bw() +
  geom_line(aes(x = date, y = rt_median), col = "deepskyblue4", size = 1.3) +
  geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue4", alpha = 0.5) +
  facet_wrap(~covid_region, scales = "free") +
  geom_hline(yintercept = 1, linetype = "dashed") +
  labs(fill = "", color = "", x = "", y = expression(italic(R[t])), caption = "method = uncertain_si") +
  scale_x_date(breaks = "30 days", date_labels = "%d\n%b") +
  customThemeNoFacet


ggsave(paste0(today, "_Rt_estimated_from_data_zoom.pdf"),
  plot = p_Rt, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0(today, "_Rt_estimated_from_data_zoom.png"),
  plot = p_Rt, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "png"
)



scl <- mean(dat$cases) / mean(Rt_dat$rt_median)
dat$date <- as.Date(dat$date)
Rt_dat$date <- as.Date(Rt_dat$date)

pplot <- ggplot(data = subset(Rt_dat, date >= "2020-04-01")) +
  theme_bw() +
  geom_bar(data = subset(dat, date >= "2020-04-01"), aes(x = date, y = cases / scl), fill = "grey", stat = "identity", alpha = 1) +
  geom_line(aes(x = date, y = rt_median), col = "deepskyblue4", size = 1) +
  geom_ribbon(aes(x = date, ymin = rt_lower, ymax = rt_upper), fill = "deepskyblue4", alpha = 0.5) +
  facet_wrap(~covid_region, scales = "free") +
  geom_hline(yintercept = 1.3, linetype = "dashed", col = "red") +
  scale_y_continuous(expression(italic(R[t])), sec.axis = sec_axis(~ . * scl, name = "Cases")) +
  labs(fill = "", color = "", x = "", y = expression(italic(R[t])), caption = "method = uncertain_si") +
  scale_x_date(breaks = "30 days", date_labels = "%d\n%b") +
  customThemeNoFacet



ggsave(paste0(today, "_Rt_and_cases_from_data.pdf"),
  plot = pplot, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "pdf"
)
ggsave(paste0(today, "_Rt_and_cases_from_data.png"),
  plot = pplot, path = file.path(outdir), width = 14, height = 8, dpi = 300, device = "png"
)
