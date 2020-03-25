###==========================================
### Project: Covid-19 Chicago
### MR
### Input:
### - predicted trajectories from cms model
### - The input csv file was already formatted running basic_output_processing.py for single run
### 
### Output:
### Explorative plots with comaprison to Illinos data
### Growth rate calculations
###
### Note: This script is for quick eplorative plots using cms outputs, 
### ideally all the figures and analysis will be done in python
###==========================================

library(tidyverse)
library(cowplot)
library(scales)

username = Sys.getenv("USERNAME")
project_dir = file.path("C:/Users/",username ,"/Box/NU-malaria-team/projects/covid_chicago")
pred <- read.csv(file.path(project_dir ,"cms_sim/illinois/illinois_v0_singleRun_dat.csv"))
pred$time=round(pred$time,0)
pred$Date = seq(as.Date("2020-03-07"), as.Date("2020-03-07") + max(pred$time)-1, "days")  ### initial importations - start of SEIR model

## Load illinois data 
dat <- read.csv(file.path(project_dir ,"Illinois_data/illinois_cases_death.csv"))
## Start counting on some time before first cases were reported, i.e. 9th of March 2020
startday <- dat$nday[dat$Date=="2020-02-25"]
dat <- dat %>%  select(nday, Date, deaths, confirmed_cases) %>% mutate(Date =  as.Date(Date)) %>% filter(Date >="2020-03-01")




##  Custom plotting theme and colors
customTheme <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.text.y = element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 14),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 16),
  axis.title.y = element_text(size = 16),
  axis.text.x = element_text(size = 16),
  axis.text.y = element_text(size = 16)
)

### Define colors
## https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=8
cols <- c(
  "susceptible" = "#1b9e77", 
  "exposed" = "#d95f02",
  "infectious" = "#7570b3", 
  "recovered" = "#e7298a",
  "hospitalized" = "#66a61e", 
  "symptomatic" = "#e6ab02", 
  "critical" = "#a6761d", 
  "death" = "#666666"
)


## Extend SEIR outcomes by calculating hospitaliszations and deaths
## Note these calculations are placed in the python script
## To do: add sample num, or export dataframe from within python script
CFR <- 0.016
fraction_symptomatic <- 0.7
fraction_hospitalized <- 0.3
fraction_critical <- 0.8
time_to_hospitalization <- 6
time_to_critical <- 6
time_to_death <- 2

fraction_death <- CFR / (fraction_hospitalized * fraction_critical)

pred["time_hospitalized"] <- pred["time"] + time_to_hospitalization
pred["time_critical"] <- pred["time_hospitalized"] + time_to_critical
pred["time_death"] <- pred["time_critical"] + time_to_death

pred["symptomatic"] <- pred["infectious"] * fraction_symptomatic
pred["hospitalized"] <- pred["symptomatic"] * fraction_hospitalized
pred["critical"] <- pred["hospitalized"] * fraction_critical
pred["death"] <- pred["critical"] * fraction_death

## Transform data to long format for plotting
plotdat <- pred %>%
  filter(time <= 90) %>%
  select(-X, ) %>%
  pivot_longer(cols = -c(time, Date, time_hospitalized, time_critical, time_death), names_to = "outcome")

plotdat$outcome <- factor(plotdat$outcome,
  levels = c("susceptible", "exposed", "infectious","symptomatic","hospitalized", "critical","death","recovered"),
  labels =  c("susceptible", "exposed", "infectious","symptomatic","hospitalized", "critical","death","recovered")
)


pSEIR <- ggplot() + theme_cowplot() +
  geom_line(
    data = subset(plotdat,outcome %in% c("susceptible", "exposed", "infectious", "recovered")),
    aes(x = Date, y = value, col = outcome), size = 1.7, alpha = 0.7
  ) +
  labs(
    subtitle = "SEIR model predictions for Illinois population",
    x = "", y = "Population [N]", color = ""
  ) +
  scale_color_manual(values = cols) +
  scale_x_date(date_breaks = "1 week", date_labels = "%d\n%b") +
  scale_y_continuous(labels=comma)+
  customTheme
print(pSEIR)

pplot_Hdat <-  ggplot() +
  theme_cowplot() +
  geom_line(
    data = subset(plotdat, time <= 30 & outcome %in% c("hospitalized", "recovered", "death")),
    aes(x = Date, y = value, col = outcome), size = 1.7, alpha = 0.7
  ) +
  geom_line(
    data = subset(dat),
    aes(x = Date, y = confirmed_cases), size = 1.7, alpha = 0.7
  ) +
  geom_point(
    data = subset(dat),
    aes(x = Date, y = confirmed_cases), shape=21,size = 1.7, alpha = 0.7
  ) +
  labs(
    subtitle = "",
    x = "", y = "Population [N]", color = ""
  ) +
  scale_color_manual(values = cols) +
  scale_x_date(date_breaks = "1 week", date_labels = "%d\n%b") +
  scale_y_continuous(labels=comma, lim=c(0,30000))+
  customTheme
print(pplot_Hdat)


ggsave("sample_plot_illinpis_SEIR.png",
       plot = pSEIR, device = "png", path = file.path(project_dir, "cms_sim/illinois"),
       width = 12, height = 8
)

ggsave("sample_plot_illinpis_withDat.png",
       plot = pplot_Hdat, device = "png", path = file.path(project_dir, "cms_sim/illinois"),
       width = 12, height = 8
)

### Calculate daily growth rates 
GrowthDat <- pred %>%
  group_by() %>%
  mutate(
    exposedGrowth = (exposed - lag(exposed)) / lag(exposed),
    infectiousGrowth = (infectious - lag(infectious)) / lag(infectious),
    hospitalizedGrowth = (hospitalized - lag(hospitalized)) / lag(hospitalized)
  ) %>%
  select(time, exposed, infectious, hospitalized, exposedGrowth, infectiousGrowth, hospitalizedGrowth)

## Plot growth rates
pGrowth <- ggplot() +
  theme_cowplot() +
  geom_line(
    data = subset(GrowthDat, time <= 60),
    aes(x = time, y = infectiousGrowth), size = 1.7, alpha = 0.7
  )
print(pGrowth)

## Average growth rates for specific time periods
growthTable <- matrix(NA, 6,2)
rownames(growthTable) <- seq(10,60,10)
colnames(growthTable) <- c("infectious", "hospitalized")

for(i in rownames(growthTable)){
  
  i_num= as.numeric(i)
  growthTable[i,] <- GrowthDat %>%
                        filter(time > 1 & time < i_num) %>%
                        summarize(infectiousGrowth = mean(infectiousGrowth),
                                  hospitalizedGrowth = mean(hospitalizedGrowth)) %>% 
                        as.numeric()

}

sink(file=file.path(project_dir, "averageDailyGrowthRate.txt"))
print(growthTable)
sink()



