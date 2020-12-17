
library(tidyverse)
library(data.table)

theme_set(theme_minimal())


runInBatchMode <- TRUE

if (runInBatchMode) {
  cmd_agrs <- commandArgs()
  length(cmd_agrs)
  exp_name <- cmd_agrs[length(cmd_agrs) - 2]
  Location <- cmd_agrs[length(cmd_agrs) - 1]
  workingDir <- cmd_agrs[length(cmd_agrs)]
} else {
  exp_name <- "20200911_IL_test_v3"
  Location <- "Local"
  workingDir <- getwd()
}

print(workingDir)
source(file.path(workingDir,"load_paths.R"))

### Set custom theme for plotting
fontscl=3
customTheme <- theme(
  strip.text.x = element_text(size = 12 + fontscl, face = "bold"),
  strip.text.y = element_text(size = 12 + fontscl, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 16 + fontscl, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 14 + fontscl),
  plot.caption = element_text(size = 10 + fontscl),
  legend.title = element_text(size = 12 + fontscl),
  legend.text = element_text(size = 12 + fontscl),
  axis.text.x = element_text(size = 11 + fontscl),
  axis.text.y = element_text(size = 11 + fontscl),
  axis.title.x = element_text(size = 12 + fontscl),
  axis.title.y = element_text(size = 12 + fontscl)
)


#### Load prevalence dat generated from plot_prevalence.py
plot_dir <- file.path(simulation_output,exp_name,"_plots")
dat <- fread(file.path(simulation_output,exp_name,"prevalenceDat.csv")) 


### Transform dataformat 
modelCols <- c("date","scen_num","run_num", "sample_num")
prevCols <- colnames(dat)[grep("prev",colnames(dat))]
keepCols <- c(modelCols, prevCols)
dat <- dat %>% filter(date==Sys.Date()) %>% 
      select_at(keepCols) %>%
      rename_with( ~ gsub("_All", "_EMS-0", .x)) %>%
      pivot_longer(cols=-c(modelCols)) %>%
      separate(name, into=c("channel", "region"), sep="_EMS-") %>%
      mutate(value=value*100) %>%
      group_by(region, channel) %>%
      summarize(            min.value = min(value, na.rm = TRUE),
                            max.value = max(value, na.rm = TRUE),
                            median.value = median(value, na.rm = TRUE),
                            q25.value = quantile(value, probs = 0.25, na.rm = TRUE),
                            q75.value = quantile(value, probs = 0.75, na.rm = TRUE),
                            q2.5.value = quantile(value, probs = 0.025, na.rm = TRUE),
                            q97.5.value = quantile(value, probs = 0.975, na.rm = TRUE)) %>%
      filter(channel=="seroprevalence") %>%
      mutate(region=as.numeric(region)) %>%
      arrange(region)


dat$region <- factor(dat$region, levels=c(0:11), 
                         labels=c("IL", c(1:11)))

#### Generate plot
pplot <- ggplot(data=subset(dat, region!="IL"))+
  geom_rect(data=subset(dat, region=="IL"), aes(xmin=-Inf, xmax=Inf, ymin=q25.value,ymax=q75.value), fill="grey", alpha=0.3)+
  geom_rect(data=subset(dat, region=="IL"), aes(xmin=-Inf, xmax=Inf, ymin=q2.5.value,ymax=q97.5.value), fill="grey", alpha=0.3)+
  geom_hline(data=subset(dat, region=="IL"), aes(yintercept=median.value), linetype="longdash")+
  geom_pointrange(aes(x=region,y=median.value,  ymin= q2.5.value, ymax=q97.5.value ),color="#f77189") +
  geom_text(data=subset(dat, region=="IL"), aes(x=1.2, y=median.value+1, label="Illinois overall"),size=5)+
  labs(y="Fraction ever infected (%)", x="COVID-19 region")+
  geom_hline(yintercept=c(Inf, -Inf)) + 
  geom_vline(xintercept=c(Inf, -Inf))+
  theme(legend.position="none",
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank())+
  customTheme

pplot

plotname=paste0("seroprevalence_by_region_",gsub("-","",Sys.Date()))
ggsave(paste0(plotname, ".png"), plot = pplot, path = plot_dir, width = 9, height = 5, device = "png")
ggsave(paste0(plotname, ".pdf"), plot = pplot, path = file.path(plot_dir, "pdf"), width = 9, height = 5, device = "pdf")


### For text
sink(file.path(simulation_output, exp_name, "seroprevalence_today.txt"))
print(Sys.Date())
print(dat)
sink()






