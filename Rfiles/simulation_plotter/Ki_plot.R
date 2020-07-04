###------------------------------------------------------------------------
#### R scriot to plot the time varying Ki parameter per EMS
###-----------------------------------------------------------------------

library(viridis)
library(tidyverse)
library(cowplot)

source("load_paths.R")

### Options for plot theme
customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 12, face = "bold"),
  strip.text.y = element_text(size = 12, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 16, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 12),
  plot.caption = element_text(size = 8),
  legend.title = element_text(size = 12),
  legend.text = element_text(size = 12),
  axis.title.x = element_text(size = 12),
  axis.text.x = element_text(size = 12),
  axis.title.y = element_text(size = 12),
  axis.text.y = element_text(size = 12)
)


### Load trajectories Dat
exp_name = "20200630_IL_1_endsip35"
Ki_dat <- read.csv(file.path(simulation_output, exp_name, "trajectoriesDat.csv"))

### Note use Ki_EMS-  or Ki_EMS.   not Ki_EMS_  (time varying vs input parameter) 
colnames(Ki_dat) <- gsub("[.]","-", colnames(Ki_dat))
Kivars <-  paste0("Ki_EMS-", c(1:11))
keepvars <- c("time", "startdate",Kivars )
 
### Wide to long format and calculate date
### Aand aggregate samples
Ki_dat <- Ki_dat %>% select(keepvars) %>% 
  mutate(date = as.Date(startdate) + time) %>%  
  pivot_longer(cols=-c("time","date","startdate"), names_to ="region") %>%
  mutate(region = gsub("EMS-","",gsub("Ki_", "", region)),
         region = as.numeric(region)) %>%
  group_by( date, region) %>%
  summarize(value = mean(value))
  


### Plot
pplot <- ggplot(data=subset(Ki_dat, date <= as.Date("2020-08-01"))) + 
  theme_cowplot() +  
  geom_line(aes(x=date, y=value,col=as.factor(region), group=region), size=1.3) +
  scale_color_viridis(discrete = TRUE) +
  labs(color="EMS", y = "Transmission rate") +
  customThemeNoFacet +
  labs(x="")

ggsave(paste0("Ki_plot.png"),
       plot = pplot, path = file.path(simulation_output, exp_name), width = 10, height = 5, device = "png"
)
