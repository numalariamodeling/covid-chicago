## ==============================================================
## R script to plot the weekly deliverables together in one plot
## ==============================================================

require(tidyverse)
require(cowplot)
require(scales)
require(data.table)
require(viridis)

runInBatchMode <- FALSE

if (runInBatchMode) {
  cmd_agrs <- commandArgs()
  length(cmd_agrs)
  Location <- cmd_agrs[length(cmd_agrs) - 1]
  workingDir <- cmd_agrs[length(cmd_agrs)]
} else {
  Location <- "Local"
  workingDir <- getwd()
}


source("load_paths.R")
source("processing_helpers.R")

exp_name <- "20201021_EMS_1_testrun_ct_2ndWave_run2"
exp_dir <- file.path(simulation_output, exp_name)



### Load trajectoriesDat
trajectories <- fread(file.path(exp_dir, "trajectoriesDat.csv"))
keepCols <- colnames(trajectories)[c(
  grep("infected", colnames(trajectories)), grep("N_", colnames(trajectories)),
  grep("recovered", colnames(trajectories)), grep("death", colnames(trajectories)),
  grep("hosp", colnames(trajectories)), grep("crit", colnames(trajectories))
)]
keepCols <- c("scen_num", "time", "startdate", keepCols[c(!(grepl("time", keepCols)))])
keepCols <- c(keepCols[c(!(grepl("fraction", keepCols)))])


trajectories <- trajectories %>%
  dplyr::select(keepCols) %>%
  pivot_longer(cols = -c("scen_num", "time", "startdate")) %>%
  mutate(
    date = as.Date(startdate) + time,
    name = gsub("All", "ageAll", name)
  ) %>%
  separate(name, into = c("outcome", "age"), sep = "_age") %>%
  mutate(age = gsub("to", " to ", age))

table(trajectories$outcome)
npop <- trajectories %>%
  dplyr::filter(outcome == "N") %>%
  select(age, value) %>%
  unique() %>%
  rename(pop = value)
trajectories <- trajectories %>%
  filter(outcome != "N") %>%
  left_join(npop, by = "age")
trajectories <- trajectories %>%
  filter(age != "All") %>%
  filter(date >= as.Date("2020-3-01") & date <= as.Date("2020-10-20"))
trajectories$date <- as.Date(trajectories$date)


#### for Area plot
trajectoriesAggr <- trajectories %>%
  group_by(date, age, pop, outcome) %>%
  summarize(value=median(value)) %>%
  ungroup() %>%
  group_by(date, outcome) %>%
  mutate(value_all = sum(value), 
         pop_all= sum(pop),
         value_perc =ifelse(value_all==0,0, value/value_all)) %>%
  group_by(outcome, age, pop) %>%
  arrange(date) %>%
  mutate(value_perc_7roll =rollapply(value_perc,7,mean,align='right',fill=NA) ) 

tapply(trajectoriesAggr$value_perc, trajectoriesAggr$outcome, summary)
tapply(trajectoriesAggr$value_perc_7roll, trajectoriesAggr$outcome, summary)



#### Heatmap
for (selected_outcome in unique(trajectories$outcome)) {
  # selected_outcome <- "infected"

  pplot <- trajectories %>% 
    filter(outcome == selected_outcome) %>%
    group_by(date, age, pop) %>%
    summarize(value=median(value)) %>%
    ggplot(y = factor(age), fill = value / pop * 1000) +
    geom_tile(aes(x = date, y = factor(age), fill = value / pop * 1000)) +
    scale_fill_viridis_c(option = "magma") +
    scale_y_discrete(expand = c(0, 0)) +
    scale_x_date(date_labels = "%b\n%d", date_breaks = "30 days", expand = c(0, 0)) +
    labs(y = "Age group", 
         x = "", 
         fill = paste0('predicted ',selected_outcome, "\nper 1000 population")) +
    geom_hline(yintercept = c(1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5), color = "white", size = 0.01, alpha = 0.3)
    

  ggsave(paste0(selected_outcome, "_age_heatmap.png"),
    plot = pplot,
    path = file.path(exp_dir, "_plots"), width = 10, height = 8, device = "png"
  )
  rm(pplot)
  
  
  pplot <- trajectoriesAggr %>%
    filter(outcome == selected_outcome &
             date >= as.Date("2020-04-01")) %>%
    ggplot(aes(x = date, y = value_perc_7roll, fill = factor(age))) + 
    geom_area() +
    geom_area(color = "white",linetype=2,size=0.2,show.legend = F, position='stack') +
    labs(fill = "Age Group", 
         x="",
         y=paste0("% of predicted ", selected_outcome), 
         caption="predicted median, 7 day rolling average") + 
    scale_fill_brewer(palette="Paired", direction = -1) +
    scale_y_continuous(expand=c(0,0))+
    scale_x_date(expand=c(0,0))
  
  ggsave(paste0(selected_outcome, "_age_area.png"),
         plot = pplot,
         path = file.path(exp_dir, "_plots"), width = 10, height = 8, device = "png"
  )
  


}


### Barplot 'today' or at any timepoint per outcome
datelabel <- max(trajectoriesAggr$date)
pplotDat <- trajectoriesAggr %>%
  filter(date ==max(date),
         outcome %in% c("infected","hosp_det","crit_det","deaths")) 

pplotDat$outcome <- factor(pplotDat$outcome, 
                           levels=c("infected","hosp_det","crit_det","deaths"),
                           labels=c("infected","hosp_det","crit_det","deaths"))

pplot <- pplotDat %>%
  ggplot(aes(x = age, y = value/pop, fill = factor(age))) + 
  theme_cowplot()+
  geom_bar( stat="identity") +
  facet_wrap(~outcome, scales="free") +
  scale_fill_brewer(palette="Paired", direction = -1) +
  labs(fill="Age group",
       y="total number per 1000 population",
       caption=paste0('date ', datelabel)) +
  # scale_y_continuous(expand=c(0,0))+
 # scale_x_discrete(expand=c(0,0))

ggsave(paste0(selected_outcome, "_age_barplot.png"),
       plot = pplot,
       path = file.path(exp_dir, "_plots"), width =14, height = 8, device = "png"
)

rm(pplotDat, pplot)




