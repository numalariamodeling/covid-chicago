## ============================================================
### Compare Rt estimates from data and from simulations
## ============================================================


library(tidyverse)
library(cowplot)

source("load_paths.R")
source("processing_helpers.R")
setwd(file.path(git_dir, "Rfiles/estimate_Rt"))


Rtdat <- read.csv(file.path("nu_il_fromdata_estimated_Rt.csv")) %>% mutate(source = "data")
Rtsim <- read.csv(file.path("nu_il_baseline_estimated_Rt.csv")) %>%
  mutate(source = "simulations") %>%
  mutate(geography_modeled = gsub("ems", "EMS_", geography_modeled)) %>%
  filter(
    Date <= "2020-10-01",
    geography_modeled %in% paste0("EMS_", c(1:11))
  )

Rtdat$Date <- as.Date(Rtdat$Date)
Rtsim$Date <- as.Date(Rtsim$Date)

Rt_comb <- as.data.frame(rbind(Rtdat, Rtsim))
tapply(Rt_comb$Date, Rt_comb$source, summary)


Rt_comb$geography_modeled <- factor(Rt_comb$geography_modeled, levels = paste0("EMS_", c(1:11)), labels = paste0("EMS_", c(1:11)))

tapply(subset(Rt_comb, Date >= as.Date("2020-03-12"))$Median.of.covid.19.Rt, subset(Rt_comb, Date >= as.Date("2020-03-12"))$source, summary)

pplot <- ggplot(data = subset(Rt_comb, Date >= as.Date("2020-03-01"))) +
  theme_cowplot() +
  geom_line(aes(x = Date, y = Median.of.covid.19.Rt, group = source), col = "grey", size = 0.7, alpha = 0.7) +
  geom_ribbon(aes(x = Date, ymin = Lower.error.bound.of.covid.19.Rt, ymax = Upper.error.bound.of.covid.19.Rt, fill = source), alpha = 0.5) +
  geom_smooth(aes(x = Date, y = Median.of.covid.19.Rt, col = source), size = 1.3, se = FALSE, span = 0.3) +
  facet_wrap(~geography_modeled, scales = "free_y") +
  customThemeNoFacet +
  labs(
    title = "Estimated Rt \n",
    y = "Estimated Rt",
    subtitle = "mean after shelter in place ~ 0.9740  \n Using EpiEstim and an uncertain serial interval distribution (mean 4.6, min 1, max 6.47 )",
    caption = "using 1 week sliding window for simulations and 2 weeks for the data when estimating Rt"
  ) +
  geom_hline(yintercept = 1, linetype = "dashed", col = "darkred", size = 1) +
  geom_vline(xintercept = c(as.Date("2020-03-12"), as.Date("2020-06-01")), linetype = "solid") +
  geom_hline(yintercept = c(-Inf, Inf)) +
  geom_vline(xintercept = c(-Inf, Inf)) +
  scale_color_manual(values = c("deepskyblue4", "darkorange")) +
  scale_fill_manual(values = c("deepskyblue4", "darkorange"))
print(pplot)

ggsave(paste0("Rt_comparison_uncertain_si.png"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "png"
)


pplot <- ggplot(data = subset(Rt_comb, source == "simulations" & Date >= as.Date("2020-03-01"))) +
  theme_cowplot() +
  geom_line(aes(x = Date, y = Median.of.covid.19.Rt, group = source), col = "grey", size = 0.7, alpha = 0.7) +
  geom_ribbon(aes(x = Date, ymin = Lower.error.bound.of.covid.19.Rt, ymax = Upper.error.bound.of.covid.19.Rt, fill = source), alpha = 0.5) +
  geom_smooth(aes(x = Date, y = Median.of.covid.19.Rt, col = source), size = 1.3, se = FALSE, span = 0.3) +
  facet_wrap(~geography_modeled, scales = "free_y") +
  customThemeNoFacet +
  labs(
    title = "Estimated Rt \n",
    y = "Estimated Rt",
    subtitle = "mean after shelter in place ~ 0.9740  \n Using EpiEstim and an uncertain serial interval distribution (mean 4.6, min 1, max 6.47 )",
    caption = "using 1 week sliding window for simulations and 2 weeks for the data when estimating Rt"
  ) +
  geom_hline(yintercept = 1, linetype = "dashed", col = "darkred", size = 1) +
  geom_vline(xintercept = c(as.Date("2020-03-12"), as.Date("2020-06-01")), linetype = "solid") +
  geom_hline(yintercept = c(-Inf, Inf)) +
  geom_vline(xintercept = c(-Inf, Inf)) +
  scale_color_manual(values = c("darkorange")) +
  scale_fill_manual(values = c("darkorange"))
print(pplot)

ggsave(paste0("Rt_simulations_uncertain_si.png"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "png"
)


pplot <- ggplot(data = subset(Rt_comb, source != "simulations" & Date >= as.Date("2020-03-01"))) +
  theme_cowplot() +
  geom_line(aes(x = Date, y = Median.of.covid.19.Rt, group = source), col = "grey", size = 0.7, alpha = 0.7) +
  geom_ribbon(aes(x = Date, ymin = Lower.error.bound.of.covid.19.Rt, ymax = Upper.error.bound.of.covid.19.Rt, fill = source), alpha = 0.5) +
  geom_smooth(aes(x = Date, y = Median.of.covid.19.Rt, col = source), size = 1.3, se = FALSE, span = 0.3) +
  facet_wrap(~geography_modeled, scales = "free_y") +
  customThemeNoFacet +
  labs(
    title = "Estimated Rt \n",
    y = "Estimated Rt",
    subtitle = "mean after shelter in place ~ 0.9740  \n Using EpiEstim and an uncertain serial interval distribution (mean 4.6, min 1, max 6.47 )",
    caption = "using 1 week sliding window for simulations and 2 weeks for the data when estimating Rt"
  ) +
  geom_hline(yintercept = 1, linetype = "dashed", col = "darkred", size = 1) +
  geom_vline(xintercept = c(as.Date("2020-03-12"), as.Date("2020-06-01")), linetype = "solid") +
  geom_hline(yintercept = c(-Inf, Inf)) +
  geom_vline(xintercept = c(-Inf, Inf)) +
  scale_color_manual(values = c("deepskyblue4")) +
  scale_fill_manual(values = c("deepskyblue4"))
print(pplot)

ggsave(paste0("Rt_data_uncertain_si.png"),
  plot = pplot, width = 14, height = 8, dpi = 300, device = "png"
)
