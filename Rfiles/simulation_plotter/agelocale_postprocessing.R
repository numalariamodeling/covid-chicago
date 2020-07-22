## ==================================================
# R script that analysis trajectoriesDat
## ==================================================

require(tidyverse)
require(cowplot)
require(scales)
require(readxl)
require(viridis)
require(stringr)
require(broom)

source("load_paths.R")
source("processing_helpers.R")


EMS_1 <- c(78641, 91701, 94681, 89371, 92396, 110878, 92988, 89076)
EMS_2 <- c(114210, 132626, 150792, 141161, 140827, 170321, 143642, 135817)
EMS_3 <- c(57069, 71489, 76506, 71437, 79844, 101522, 82573, 81032)
EMS_4 <- c(72063, 84167, 89843, 88706, 89248, 110692, 87058, 79757)
EMS_5 <- c(41533, 48068, 55005, 48713, 49212, 64576, 54930, 57281)
EMS_6 <- c(78524, 92005, 119387, 96035, 94670, 117353, 99559, 94750)
EMS_7 <- c(208260, 251603, 217013, 238956, 251248, 280849, 206843, 171112)
EMS_8 <- c(187495, 218993, 204630, 235119, 233866, 258661, 190207, 154577)
EMS_9 <- c(223250, 259507, 232036, 274367, 284363, 307266, 221915, 177803)
EMS_10 <- c(113783, 138714, 118833, 134124, 147069, 166857, 127055, 111866)
EMS_11 <-  c(326312, 330144, 432323, 457425, 349783, 347788, 270747, 230158)

popdat = as.data.frame(cbind(EMS_1, EMS_2, EMS_3,EMS_4, EMS_5, EMS_6,EMS_7, EMS_8, EMS_9,EMS_10, EMS_11))
popdat$age = c("age0to9", "age10to19", "age20to29", "age30to39", "age40to49", "age50to59", "age60to69", "age70to100")
popdat<- popdat %>% pivot_longer(cols=-age, names_to="region", values_to="N") %>% 
  mutate(region = gsub("EMS_","", region),
         age = gsub("age","", age))

simdir <- file.path(simulation_output)
exp_dir <- "20200624_IL_agelocale_migration_test2"
trajectoriesDat <- read.csv(file.path(simulation_output, exp_dir, "trajectoriesDat.csv"))

# emsvars <- colnames(trajectoriesDat)[grep("[.]",colnames(trajectoriesDat))]
emsvars_temp <- c("infected_age0to9_EMS.",  "asymptomatic_age0to9_EMS.", "critical_age0to9_EMS." , "deaths_age0to9_EMS.",
                  "infected_age10to19_EMS.",  "asymptomatic_age10to19_EMS.", "critical_age10to19_EMS." , "deaths_age10to19_EMS.",
                  "infected_age20to29_EMS.",  "asymptomatic_age20to29_EMS.", "critical_age20to29_EMS." , "deathsage20to29_EMS.",
                  "infected_age30to39_EMS.",  "asymptomatic_age30to39_EMS.", "critical_age30to39_EMS." , "deaths_age30to39_EMS.",
                  "infected_age40to49_EMS.",  "asymptomatic_age40to49_EMS.", "critical_age40to49_EMS." , "deaths_age40to49_EMS.",
                  "infected_age50to59_EMS.",  "asymptomatic_age50to59_EMS.", "critical_age50to59_EMS." , "deaths_age50to59_EMS.",
                  "infected_age60to69_EMS.",  "asymptomatic_age60to69_EMS.", "critical_age60to69_EMS." , "deaths_age60to69_EMS.",
                  "infected_age70to100_EMS.",  "asymptomatic_age70to100_EMS.", "critical_age70to100_EMS." , "deaths_age70to100_EMS.")

emsvars <- NULL
for (ems in c(1:11)) {
  emsvars <- c(emsvars, paste0(emsvars_temp, ems))
}

groupvars <- c("time", "startdate", "scen_num", "sample_num", "run_num")
(keepvars <- c(groupvars, emsvars))


subdat <- trajectoriesDat[,colnames(trajectoriesDat) %in% keepvars ] 

subdat2 <- subdat %>%
  pivot_longer(cols = -c(groupvars)) %>%
  mutate(
    startdate = as.Date(startdate),
    Date = as.Date(time + startdate),
  ) %>%
  separate(name, into = c("outcome_age", "region"), sep = "_EMS[.]")%>%
separate(outcome_age, into = c("outcome", "age"), sep = "_age")


head( subdat2)


subdat2$outcome = factor(subdat2$outcome , levels= c("infected", "asymptomatic", "critical", "deaths"), labels=c("infected", "asymptomatic", "critical", "deaths"))
subdat2$age2 = factor(subdat2$age , levels= rev(unique(subdat2$age)), labels=rev(unique(subdat2$age)))
subdat2$region2 = factor(subdat2$region , levels=c(1:11), labels=paste0("EMS_",c(1:11)))

popdat=as.data.frame(popdat)
subdat2 <- subdat2 %>% left_join(popdat, by=c("age","region"))
subdat2$value_scl = (subdat2$value / subdat2$N) * 100000

subdat2Aggr = subdat2 %>% 
                group_by(Date, outcome, region,region2, age,age2, N) %>% 
                summarize(value=mean(value), value_scl = mean(value_scl))

pplot_area1 <- ggplot(data= subset(subdat2Aggr, Date>=as.Date("2020-03-23") & Date<as.Date("2020-10-25")& outcome=="infected")) + 
  theme_minimal() +customFonts+
  geom_area(aes(x=Date, y=value_scl,fill=age2, group=age2), stat="identity", position="stack") +
  facet_wrap(~region2, scales="free")+
  scale_fill_brewer(palette = "RdYlBu")+
  labs(color="Age group", 
       fill="Age group", y="infected",
       title="Predicted infected cases due to COVID-19 per age and EMS region \n", 
       subtitle="Scaled per 100.000 population")

pplot_area2 <- ggplot(data= subset(subdat2Aggr, Date>=as.Date("2020-03-23") & Date<as.Date("2020-10-25")& outcome=="asymptomatic")) + 
  theme_minimal() +customFonts+
  geom_area(aes(x=Date, y=value_scl,fill=age2, group=age2), stat="identity", position="stack") +
  facet_wrap(~region2, scales="free")+
  scale_fill_brewer(palette = "RdYlBu")+
  labs(color="Age group", fill="Age group", y="infected",
       title="Predicted asymptomatic cases due to COVID-19 per age and EMS region", 
       subtitle="Scaled per 100.000 population")


pplot_area3 <- ggplot(data= subset(subdat2Aggr, Date>=as.Date("2020-03-23") & Date<as.Date("2020-10-25")& outcome=="deaths")) + 
  theme_minimal() +customFonts+
  geom_area(aes(x=Date, y=value_scl,fill=age2, group=age2), stat="identity", position="stack") +
  facet_wrap(~region2, scales="free")+
  scale_fill_brewer(palette = "RdYlBu")+
  labs(color="Age group", fill="Age group", y="deaths",
       title="Predicted deaths due to COVID-19 per age and EMS region", subtitle="Scaled per 100.000 population")


pplot_bar <- ggplot(data= subset(subdat2, Date>=as.Date("2020-06-23") & Date<as.Date("2020-06-25")&
                      outcome  %in% c("infected", "asymptomatic", "critical", "deaths"))) + 
  theme_minimal() +customFonts+
  geom_bar(aes(x=as.numeric(region), y=value, group=age2, fill=age2),position="stack", stat="identity") +
  facet_wrap(~outcome, scales="free", ncol=2)+
  scale_fill_brewer(palette = "RdYlBu")+
  scale_x_continuous(breaks=c(1:11), labels=c(1:11)) + 
  scale_y_continuous(expand=c(0,0))+
  labs(y="Total number of population",x="EMS region",fill="Age group",
       title="Predicted COVID-19 outcomes per age and EMS region", subtitle="Simulation date: 2020-06-23")

pplot_bar_scl <- ggplot(data= subset(subdat2, Date>=as.Date("2020-06-23") & Date<as.Date("2020-06-25")&
                                   outcome  %in% c("infected", "asymptomatic", "critical", "deaths"))) + 
  theme_minimal() +customFonts+
  geom_bar(aes(x=as.numeric(region), y=value_scl, group=age2, fill=age2),position="stack", stat="identity") +
  facet_wrap(~outcome, scales="free", ncol=2)+
  scale_fill_brewer(palette = "RdYlBu")+
  scale_x_continuous(breaks=c(1:11), labels=c(1:11)) + 
  scale_y_continuous(expand=c(0,0))+
  labs(y="Total number of population\nper 100.000 population",x="EMS region",fill="Age group",
       title="Predicted COVID-19 outcomes per age and EMS region", 
       subtitle="Simulation date: 2020-06-23")



ggsave("pplot_area1.png", plot = pplot_area1, path = file.path(simulation_output, exp_dir), width = 16, height = 10, device = "png")
ggsave("pplot_area2.png", plot = pplot_area2, path = file.path(simulation_output, exp_dir), width = 16, height = 10, device = "png")
ggsave("pplot_area3.png", plot = pplot_area3, path =  file.path(simulation_output, exp_dir), width = 16, height = 10, device = "png")
ggsave("pplot_bar.png", plot = pplot_bar, path =  file.path(simulation_output, exp_dir), width = 16, height = 10, device = "png")
ggsave("pplot_bar_scl.png", plot = pplot_bar_scl, path =  file.path(simulation_output, exp_dir), width = 16, height = 10, device = "png")




