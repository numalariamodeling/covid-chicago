#-------------------------------
# Title     : COVID-19
# Objective : Vaccine forward scenarios
#-------------------------------

require(data.table)
require(tidyverse)
require(cowplot)
require(scales)

setwd('Rfiles')
source("load_paths.R")
source('processing_helpers.R')

dat <- fread(file.path(data_path, 'covid_IDPH','Corona virus reports','vaccinations_by_covidregion.csv'))
dat$date <- as.Date(dat$date)

## Set dates
vaccine_past_start <- as.Date('2020-12-20')
vaccine_past_end <- max(dat$date )
vaccine_fut_start <- vaccine_past_end
vaccine_fut_end <- as.Date('2021-06-01')
target_increase <- c(2)

### Linear model by COVID-19 region
lmdat_list <- list()
for(reg in c(1:11)){
  dat_i <- dat %>%
    filter(region==reg) %>%
    select(date,persons_first_vaccinated)

  model = lm(persons_first_vaccinated ~ date,  data=dat_i)
  dates <- seq(from=vaccine_past_start,to=vaccine_fut_end, by='days')
  xdat = as.data.frame(dates)
  colnames(xdat)='date'

  xdat$persons_first_vaccinated <- predict(model,xdat)
  xdat$persons_first_vaccinated[xdat$persons_first_vaccinated <0] <-0
  xdat$model='predicted'
  xdat$region = reg
  xdat$scenario = 'continued'
  lmdat_list[[reg]] = xdat
  rm(dat_i)
}
lmdat_continued <- lmdat_list %>% bind_rows()
rm(lmdat_list)

### Linear model, doubled
lmdat_list <- list()
for(reg in c(1:11)){

  t = lmdat_continued %>%
    filter(region==reg & date == vaccine_fut_end) %>%
    mutate(t=persons_first_vaccinated * 2) %>%
    select(t) %>% as.numeric()

  dat_i <- dat %>%
    filter(region==reg) %>%
    select(date,persons_first_vaccinated)

  dt_scen <- as.data.frame(cbind('date'=vaccine_fut_end, 'persons_first_vaccinated'=t))
  dt_scen$date <- as.Date(dt_scen$date, origin = as.Date('1970-01-01'))

  dat_i <- dat_i %>%
    filter(date ==max(date)) %>%
    select(date,persons_first_vaccinated)

  dat_i <- rbind(dat_i,dt_scen)
  model = lm(persons_first_vaccinated ~ date,  data=dat_i)
  dates <- seq(from=vaccine_fut_start,to=vaccine_fut_end, by='days')
  xdat = as.data.frame(dates)
  colnames(xdat)='date'
  xdat$persons_first_vaccinated <- predict(model,xdat)
  xdat$persons_first_vaccinated[xdat$persons_first_vaccinated <0] <-0
  xdat$model='predicted'
  xdat$region = reg
  xdat$scenario = 'doubled'
  lmdat_list[[length(lmdat_list)+1]] = xdat
  }
lmdat_scenario <- lmdat_list %>% bind_rows()

##--------------------------------------------
### Combine and add population
##--------------------------------------------
popdat <- as.data.frame(cbind(c(1:11),c(660965,1243906, 556776, 656946, 403659, 739098, 800605, 1455324, 1004309, 2693959, 2456274)))
colnames(popdat) <- c("region","pop")

lmdat <- as.data.frame( rbind(lmdat_continued, lmdat_scenario)) %>% left_join( popdat, by="region")
lmdat$persons_first_vaccinated_raw <- lmdat$persons_first_vaccinated
lmdat <- lmdat %>% mutate(persons_first_vaccinated = ifelse(persons_first_vaccinated>pop,pop,persons_first_vaccinated))
tapply(lmdat$persons_first_vaccinated,lmdat$scenario, summary)

lmdat <- lmdat %>%
  as.data.frame() %>%
  arrange(region,pop,scenario, date) %>%
  group_by(region,pop, scenario) %>%
  mutate(remaining_susceptible = pop - persons_first_vaccinated,
         daily_first_vacc = persons_first_vaccinated - lag(persons_first_vaccinated),
         daily_first_vacc = ifelse(is.na(daily_first_vacc),0,daily_first_vacc),
         daily_first_vacc_perc =  daily_first_vacc /remaining_susceptible,
         daily_first_vacc_perc = ifelse(is.na(daily_first_vacc_perc),0,daily_first_vacc_perc),
         daily_first_vacc_perc = ifelse(is.infinite(daily_first_vacc_perc),0,daily_first_vacc_perc))

summary(lmdat$date)
lmdat[duplicated(lmdat[,c("date","region","scenario")]),c("date","region","scenario")]

 ggplot(data=subset(lmdat))+
  geom_line(aes(x=date, y=persons_first_vaccinated, col=as.factor(scenario),group=scenario))+
  theme_bw()+
  facet_wrap(~region, scales="free")+
  scale_y_continuous(labels=comma)+
  labs(title="", color="scenario",x="")

 ggplot(data=subset(lmdat))+
  geom_line(aes(x=date, y=daily_first_vacc_perc, col=as.factor(scenario),group=scenario))+
  theme_bw()+
  facet_wrap(~region, scales="free")+
  scale_y_continuous(labels=comma)+
  labs(title="", color="scenario",x="")

table(lmdat$scenario)
lmdat$scenario <- factor(lmdat$scenario,
                          levels=c('continued','doubled'),
                          labels=c('continued_trend','doubled_trend'))

lmdat %>% filter(date <= vaccine_past_end & scenario=='continued_trend') %>%
  fwrite(file.path(git_dir,'experiment_configs','input_csv','vaccination_historical.csv'))

lmdat %>% filter(scenario=='continued_trend') %>%
  fwrite(file.path(git_dir,'experiment_configs','input_csv','vaccination_linear.csv'))

lmdat %>%
  filter((scenario=='continued_trend' & date < vaccine_past_end) |
           (scenario=='doubled_trend' & date >= vaccine_past_end)) %>%
  fwrite(file.path(git_dir,'experiment_configs','input_csv','vaccination_linear_doubled.csv'))

lmdat %>%
  group_by(region,scenario) %>%
  filter(date ==max(date)) %>%
  summarize(mean=mean(persons_first_vaccinated/pop)*100) %>%
  pivot_wider(names_from=scenario , values_from=mean)


### Plots
f_custom_plot <- function(channel='persons_first_vaccinated'){
  lmdat <- as.data.frame(lmdat)
  lmdat[,'channel'] <- lmdat[,colnames(lmdat)==channel]
  lmdat[,'channel'] <- as.numeric( lmdat[,'channel'])

  pplot <- ggplot(data=lmdat)+
  geom_hline(data=popdat,aes(yintercept=pop))+
  geom_label(data=popdat,aes(y=pop, x=as.Date('2021-02-01'), label='total population'))+
  geom_line(data=subset(lmdat, date < vaccine_fut_end),
            aes(x=date, y=channel,col=scenario, group=scenario),size=1.3)+
  geom_point(data=dat,aes(x=date, y=channel),col='black',size=0.8)+
  theme_cowplot()+
  customThemeNoFacet+
  facet_wrap(~region, scales="free")+
  scale_y_continuous(labels=comma)+
  scale_x_date(date_labels = "%m")+
  scale_color_manual(values=c('#add2c8','#00a08a'))+
  labs(title="Total population that received 1st dose of a COVID-19 vaccine in Illinois by region",
       subtitle='Assumed future scenarios\n',
       color="scenario",
       x="Month 2021",
       y=channel)+
  theme(legend.position = "top")

ggsave(paste0(channel,".png"),
       plot = pplot,
       path = file.path(wdir, "parameters","vaccinations"), width = 14, height = 10, device = "png"
)
ggsave(paste0(channel,".pdf"),
       plot = pplot,
       path = file.path(wdir,  "parameters","vaccinations"), width = 14, height = 10, device = "pdf"
)

}

f_custom_plot(channel='persons_first_vaccinated')
f_custom_plot(channel='daily_first_vacc_perc')


lmdatAggr <- lmdat %>% group_by(date,scenario) %>%
  summarize(pop=sum(pop),
            persons_first_vaccinated=sum(persons_first_vaccinated),
            daily_first_vacc_perc=sum(daily_first_vacc_perc))

pplot <- ggplot(data=lmdatAggr)+
  geom_hline(aes(yintercept=pop))+
  geom_label(aes(y=pop, x=as.Date('2021-02-01'), label='total population'))+
  geom_line(data=subset(lmdatAggr,  date>vaccine_past_start & date<vaccine_fut_end),aes(x=date, y=persons_first_vaccinated,col=scenario, group=scenario),size=1.3)+
  theme_cowplot()+
  customThemeNoFacet+
  scale_y_continuous(labels=comma)+
  scale_x_date(date_labels = "%m")+
  scale_color_manual(values=c('#add2c8','#00a08a'))+
  labs(title="Percent of susceptible population that received 1st dose of a COVID-19 vaccine in Illinois by region",
       subtitle='Assumed future scenarios\n',
       color="scenario",
       x="Month 2021",
       y="Percent of susceptible population daily vaccinated")+
  theme(legend.position = "top")

ggsave("IL_vaccination_scale_up.png",
       plot = pplot,
       path = file.path(wdir, "parameters","vaccinations"), width = 14, height = 10, device = "png"
)
ggsave("IL_vaccination_scale_up.pdf",
       plot = pplot,
       path = file.path(wdir,  "parameters","vaccinations"), width = 14, height = 10, device = "pdf"
)