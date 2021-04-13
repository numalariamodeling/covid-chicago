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

dat <- fread(file.path(data_path, 'covid_IDPH','Corona virus reports','vaccinations_by_age_covidregion.csv'))
dat$date <- as.Date(dat$date)
dat <- dat %>% filter(agegrp=="65+")

### Account for time difference between getting vaccinated and vaccine being effective
### Consider a delay of 21 days
dat$date_gotvacc <- dat$date
dat$date <- dat$date + 21

## Set dates
vaccine_past_start <- as.Date('2020-12-20') + 21
vaccine_past_end <- max(dat$date )
vaccine_fut_start <- vaccine_past_end
vaccine_fut_end <- as.Date('2021-12-31')
target_increase <- c(2)

### Linear model by COVID-19 region
lmdat_list <- list()
for(reg in c(1:11)){
  dat_i <- dat %>%
    filter(covid_region==reg) %>%
    dplyr::select(date,population,persons_first_vaccinated)

  model = lm(persons_first_vaccinated ~ date,  data=dat_i)
  dates <- seq(from=vaccine_past_start,to=vaccine_fut_end, by='days')
  xdat = as.data.frame(dates)
  colnames(xdat)='date'

  xdat$persons_first_vaccinated <- predict(model,xdat)
  xdat$persons_first_vaccinated[xdat$persons_first_vaccinated <0] <-0
  xdat$model='predicted'
  xdat$covid_region = reg
  xdat$scenario = 'continued'
  xdat$pop = as.numeric(unique(dat_i[,'population']))
  lmdat_list[[reg]] = xdat
  rm(dat_i)
}
lmdat_continued <- lmdat_list %>% bind_rows()
rm(lmdat_list)


##--------------------------------------------
### Combine and add population
##--------------------------------------------

lmdat <- as.data.frame( lmdat_continued)
lmdat$persons_first_vaccinated_raw <- lmdat$persons_first_vaccinated
lmdat <- lmdat %>% mutate(persons_first_vaccinated = ifelse(persons_first_vaccinated>pop,pop,persons_first_vaccinated))
tapply(lmdat$persons_first_vaccinated,lmdat$scenario, summary)

lmdat <- lmdat %>%
  as.data.frame() %>%
  arrange(covid_region,pop,scenario, date) %>%
  group_by(covid_region,pop, scenario) %>%
  mutate(persons_first_vaccinated_perc = persons_first_vaccinated / pop,
         remaining_susceptible = pop - persons_first_vaccinated,
         daily_first_vacc = persons_first_vaccinated - lag(persons_first_vaccinated),
         daily_first_vacc = ifelse(is.na(daily_first_vacc),0,daily_first_vacc),
         daily_first_vacc_perc =  daily_first_vacc /remaining_susceptible,
         daily_first_vacc_perc = ifelse(daily_first_vacc_perc>1,1,daily_first_vacc_perc),
         daily_first_vacc_perc = ifelse(is.na(daily_first_vacc_perc),0,daily_first_vacc_perc),
         daily_first_vacc_perc = ifelse(is.infinite(daily_first_vacc_perc),0,daily_first_vacc_perc))

summary(lmdat$date)
summary(lmdat$daily_first_vacc_perc)
lmdat[duplicated(lmdat[,c("date","covid_region","scenario")]),c("date","covid_region","scenario")]

 ggplot(data=subset(lmdat))+
   geom_hline(yintercept = 0.5)+
  geom_line(aes(x=date, y=persons_first_vaccinated_perc, col=as.factor(scenario),group=scenario))+
  geom_point(data=dat,aes(x=date_gotvacc, y=persons_first_vaccinated/population))+
   scale_x_date(date_breaks = "1 month", date_labels = "%b", lim=c(as.Date("2021-01-01"), as.Date("2021-07-01")))+
   theme_bw()+
  facet_wrap(~covid_region, scales="free")+
  scale_y_continuous(labels=comma)+
  labs(title="", color="scenario",x="",caption='Assuming a 21 days delay between vaccination and effectiveness')


table(lmdat$scenario)
lmdat$scenario <- factor(lmdat$scenario,
                          levels=c('continued','doubled'),
                          labels=c('continued_trend','doubled_trend'))

#lmdat %>% filter(date <= vaccine_past_end & scenario=='continued_trend') %>%
#  fwrite(file.path(git_dir, "experiment_configs","input_csv",'vaccination_historical.csv'))


lmdat %>%  dplyr::select(date,covid_region,persons_first_vaccinated_perc) %>%
  rename(persons_above65_first_vaccinated_perc=persons_first_vaccinated_perc) %>%
    group_by(covid_region,persons_above65_first_vaccinated_perc)%>%
  filter(date==min(date)) %>%
  fwrite(file.path(git_dir, "experiment_configs","input_csv",'vaccination_fractionSevere_adjustment.csv'))

lmdat %>%  dplyr::select(date,covid_region,persons_first_vaccinated_perc) %>%
  group_by(date) %>%
  summarize(persons_first_vaccinated_perc=mean(persons_first_vaccinated_perc)) %>%
  group_by(persons_first_vaccinated_perc)%>%
  filter(date==min(date)) %>%
  rename(persons_above65_first_vaccinated_perc=persons_first_vaccinated_perc) %>%
  fwrite(file.path(git_dir, "experiment_configs","input_csv",'vaccination_fractionSevere_adjustment_IL.csv'))

lmdat %>%
  group_by(covid_region,scenario) %>%
  filter(date ==Sys.Date()+90) %>%
  summarize(mean=mean(persons_first_vaccinated_perc/pop)*100) %>%
  pivot_wider(names_from=scenario , values_from=mean)


### Plots
f_custom_plot <- function(channel='persons_first_vaccinated',SAVE=TRUE){
  lmdat <- as.data.frame(lmdat)
  lmdat[,'channel'] <- as.numeric(lmdat[,colnames(lmdat)==channel])

  dat <- as.data.frame(dat)
  dat[,'channel'] <- as.numeric(dat[,colnames(dat)==channel])


  pplot_pop = ggplot(data=lmdat)+
   geom_hline(yintercept=c(1,0.8))

  pplot <- pplot_pop +
  geom_line(data=subset(lmdat, date < vaccine_fut_end),
            aes(x=date, y=channel,col=scenario, group=scenario),size=1.3)+
  geom_point(data=dat,aes(x=date_gotvacc, y=channel),col='black',size=0.8)+
  theme_cowplot()+
  background_grid()+
  facet_wrap(~covid_region, scales="free")+
  scale_y_continuous(labels=comma)+
  scale_x_date(date_labels = "%b", date_breaks="2 month")+
  scale_color_manual(values=c('#add2c8','#00a08a'))+
  labs(title="",
       subtitle='Assumed future vaccination scenarios per COVID-19 Region in Illinois\nFor population ABOVE 65 years',
       color="scenario",
       x="Month 2021",
       y=channel,
       caption=paste0('Assuming a 21 days delay between vaccination and effectiveness\nDate generated: ',Sys.Date()))+
  theme(legend.position = "top")+
    customThemeNoFacet

if(SAVE){
  ggsave(paste0(channel,"_above65.png"),
       plot = pplot,
       path = file.path(wdir, "parameters","vaccinations"), width = 21, height = 10, device = "png"
)
ggsave(paste0(channel,"_above65.pdf"),
       plot = pplot,
       path = file.path(wdir,  "parameters","vaccinations","pdf"), width = 21, height = 10, device = "pdf"
)
}
return(pplot)
}

f_custom_plot(channel='persons_first_vaccinated_perc')


lmdatAggr <- lmdat %>% group_by(date,scenario) %>%
  summarize(persons_first_vaccinated_perc=mean(persons_first_vaccinated_perc))

datAggr <- dat %>% group_by(date_gotvacc) %>%
  summarize(persons_first_vaccinated_perc=mean(persons_first_vaccinated_perc))

pplot <- ggplot(data=lmdatAggr)+
  geom_line(data=subset(lmdatAggr,  date>vaccine_past_start & date<vaccine_fut_end),aes(x=date, y=persons_first_vaccinated_perc,col=scenario, group=scenario),size=1.3)+
  geom_point(data=datAggr,aes(x=date_gotvacc, y=persons_first_vaccinated_perc),col='black',size=0.8)+
  theme_cowplot()+
  background_grid()+
  scale_y_continuous(labels=comma)+
  scale_x_date(date_labels = "%b", date_breaks = "1 month")+
  scale_color_manual(values=c('#add2c8','#00a08a'))+
  labs(title="",
       subtitle='Assumed future vaccination scenarios for Illinois\n',
       color="scenario",
       x="Month 2021",
       y="Fraction of population ABOVE 65 years who received single vaccine dose",
       caption=paste0('Assuming a 21 days delay between vaccination and effectiveness\nDate generated: ',Sys.Date()))+
  theme(legend.position = "top")

ggsave("IL_vaccination_scale_up_ageABOVE65.png",
       plot = pplot,
       path = file.path(wdir, "parameters","vaccinations"), width = 8, height = 6, device = "png"
)
ggsave("IL_vaccination_scale_up_ageABOVE65.pdf",
       plot = pplot,
       path = file.path(wdir,  "parameters","vaccinations","pdf"), width = 8, height = 6, device = "pdf"
)

