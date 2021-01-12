## ==================================================
# R script that analysis trajectoriesDat
## ==================================================

require(tidyverse)
require(cowplot)
require(scales)
require(lattice)
require(readxl)
require(viridis)
require(stringr)
require(ggrepel)
require(data.table)

source("load_paths.R")
source("processing_helpers.R")

sim_dir <- file.path(simulation_output)
simdate <- "20200630"
exp_names <- list.dirs(file.path(sim_dir), recursive = FALSE, full.names = FALSE)


for (endsip in c("endsip17", "endsip35")) {
  #endsip = "endsip17"
  exp_names <- list.dirs(file.path(sim_dir), recursive = FALSE, full.names = FALSE)
  exp_names <- exp_names[grep(endsip, exp_names)][1:4]

  count <- 0
  for (exp_name in exp_names) {
    # exp_name <- exp_names[1]
    count <- count + 1

    exp_dir <- file.path(sim_dir, exp_name)

    trajectoriesDat <- read.csv(file.path(exp_dir, "trajectoriesDat.csv"))
    
    outcomeVars <- colnames(trajectoriesDat)[grep("_All", colnames(trajectoriesDat))]
    groupvars <- c("startdate", "time", "backtonormal_multiplier", "scen_num", "sample_num", "run_num")
    (keepvars <- c(groupvars, outcomeVars))

    trajectoriesDat <- trajectoriesDat %>%
      dplyr::select(keepvars) %>%
      mutate(
        startdate = as.Date(startdate),
        Date = as.Date(time + startdate)
      )

    trajectoriesDat$exp_name <- exp_name
    if (count == 1) datAll <- trajectoriesDat
    if (count > 1) datAll <- rbind(datAll, trajectoriesDat)
  }


  datAllsub <- subset(datAll, Date > as.Date("2021-03-01") & Date <= as.Date("2021-03-02"))
  table(datAllsub$exp_name)

  datAllsub$exp_name <- gsub("20200630_IL_", "", datAllsub$exp_name)
  datAllsub$exp_name <- gsub(paste0(endsip, "_"), "", datAllsub$exp_name)
  datAllsub$exp_name <- gsub(endsip, "endsip", datAllsub$exp_name)

  ## aggregate
  p1 <- f_aggrDat(datAllsub, c("exp_name"), "deaths_All") %>%
    ggplot() +
    theme_minimal() +
    customThemeNoFacet +
    geom_bar(aes(x = exp_name, y = mean.val), stat = "identity", width = 0.7, fill = "deepskyblue3") +
    geom_errorbar(aes(x = exp_name, ymin = lower.ci.val, ymax = upper.ci.val), width = 0.3) +
    scale_y_continuous(labels = comma, breaks = seq(0, 12e5, 2e4)) +
    labs(x = "", y = "all deaths") +
    theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank())


  ggsave(paste0(endsip, "_scenario_barplot_cumuldeathsAll.png"),
    plot = p1, path = file.path(sim_dir, "20200701_scenarios"), width = 8, height = 5, dpi = 200, device = "png"
  )
  ggsave(paste0(endsip, "_scenario_barplot_cumuldeathsAll.png"),
    plot = p1, path = file.path(sim_dir, "20200701_scenarios"), width = 8, height = 5, dpi = 200, device = "pdf"
  )

  ### Calculate deaths averted
  datAllAggr <- datAllsub %>%
    f_aggrDat(c("exp_name"), "deaths_All") %>%
    as.data.frame() %>%
    data.table()
  datAllAggr[, mean.deathsAverted := mean.val - mean.val[exp_name == "1_endsip"]]
  datAllAggr[, mean.deathsAverted_perc := (1 - (mean.val / mean.val[exp_name == "1_endsip"])) * 100]
  datAllAggr <- as.data.frame(datAllAggr)


  if (endsip == "endsip17") endsip17dat <- datAllAggr
  if (endsip == "endsip35") endsip35dat <- datAllAggr
}



##### Combined
endsip17dat$endsip <- 17
endsip35dat$endsip <- 35

datAllsub <- as.data.frame(rbind(endsip17dat, endsip35dat))

datAllsub$exp_name <- gsub("_endsip17", "_endsip", datAllsub$exp_name)
datAllsub$exp_name <- gsub("_endsip35", "_endsip", datAllsub$exp_name)

## aggregate
p1 <- datAllsub %>%
  filter(exp_name != "5_HSimprov_CTgradual") %>%
  ggplot() +
  theme_minimal() +
  customThemeNoFacet +
  geom_bar(aes(x = exp_name, y = mean.val, group = endsip, fill = endsip), stat = "identity", position = position_dodge(.9), width = 0.7) +
  geom_errorbar(aes(x = exp_name, ymin = lower.ci.val, ymax = upper.ci.val, group = endsip), width = 0.3, position = position_dodge(.9), ) +
  scale_y_continuous(labels = comma, breaks = seq(0, 12e5, 2e4)) +
  labs(x = "", y = "all deaths") +
  theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank())



datAllsub %>% select(exp_name, endsip, mean.val, mean.deathsAverted, mean.deathsAverted_perc)

datAllsub%>%
  select(exp_name, endsip, mean.val, mean.deathsAverted, mean.deathsAverted_perc) %>%
  pivot_wider(names_from = endsip, values_from = c(mean.val, mean.deathsAverted, mean.deathsAverted_perc))


ggsave("endsipALL_scenario_barplot_cumuldeathsAll.png",
  plot = p1, path = file.path(sim_dir, "20200701_scenarios"), width = 8, height = 5, dpi = 200, device = "png"
)
ggsave("endsipALL_scenario_barplot_cumuldeathsAll.pdf",
  plot = p1, path = file.path(sim_dir, "20200701_scenarios"), width = 8, height = 5, dpi = 200, device = "pdf"
)
