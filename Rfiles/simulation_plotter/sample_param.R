



sampleParam <- c("time_to_infectious",	"d_Sym_ct1" , "d_As_ct1", "reduced_inf_of_det_cases_ct1","reduced_inf_of_det_cases",
                 "time_to_symptoms",	"time_to_hospitalization",	"time_to_critical",	
                 "time_to_death",'recovery_time_asymp'	,'recovery_time_mild',	'recovery_time_hosp',
                 'recovery_time_crit',	'fraction_symptomatic',	'fraction_severe',	'fraction_critical',	
                 'cfr',	'd_Sym',	'd_Sys',	'd_As',	'd_P')


sampled_parameters <- read.csv("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/contact_tracing/20200609_AsP0/20200609_IL_EMS_AsP0_rS6_heatmap/sampled_parameters.csv")
trajectoriesDat <- read.csv("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/contact_tracing/20200609_AsP0/20200609_IL_EMS_AsP0_rS6_heatmap/trajectoriesDat.csv")
# sampled_parameters <- read.csv("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/forFitting/20200525_EMS_8_fit_test1/sampled_parameters.csv")
# trajectoriesDat <- read.csv("C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/forFitting/20200525_EMS_8_fit_test1/trajectoriesDat.csv")



sampleDatAll <- sampled_parameters %>% dplyr::select(c(scen_num,time_to_infectious,	time_to_detection,d_Sym_ct1, d_As_ct1, reduced_inf_of_det_cases, 
                                                 time_to_symptoms,	time_to_hospitalization,	time_to_critical,	reduced_inf_of_det_cases_ct1,
                                                 time_to_death,recovery_time_asymp	,recovery_time_mild,	recovery_time_hosp,
                                                 recovery_time_crit,	fraction_symptomatic,	fraction_severe,	fraction_critical,	
                                                 cfr,	d_Sym,	d_Sys,	d_As,	d_P)) %>% 
  unique()




sampleDat <- trajectoriesDat %>% dplyr::select(c(scen_num,time_to_infectious,	time_to_detection,d_Sym_ct1, d_As_ct1, reduced_inf_of_det_cases,
                                                 time_to_symptoms,	time_to_hospitalization,	time_to_critical,	reduced_inf_of_det_cases_ct1,
                                                 time_to_death,recovery_time_asymp	,recovery_time_mild,	recovery_time_hosp,
                                                 recovery_time_crit,	fraction_symptomatic,	fraction_severe,	fraction_critical,	
                                                 cfr,	d_Sym,	d_Sys,	d_As,	d_P)) %>% 
  unique()


unique(sampleDat$time_to_detection)
#apply(sampleDat, 2, summary)
summary(sampleDat)

summary(subset(sampleDat, time_to_detection == unique(sampleDat$time_to_detection)[1] ))
summary(subset(sampleDat, time_to_detection == unique(sampleDat$time_to_detection)[2] ))
summary(subset(sampleDat, time_to_detection == unique(sampleDat$time_to_detection)[3] ))



sampleDatAll_long <- sampleDatAll %>% group_by(time_to_detection) %>% pivot_longer(cols=-c(time_to_detection, scen_num)) %>% mutate(dat1="all")

sampleDat_long <- sampleDat %>% group_by(time_to_detection) %>% pivot_longer(cols=-c(time_to_detection, scen_num))  %>% mutate(dat2="success")

sampleDatAll2 <- left_join(sampleDatAll_long, sampleDat_long, by=c("scen_num", "time_to_detection", "name",'value'))  %>% 
                mutate(dat2=ifelse(is.na(dat2),"no",dat2) ,status=ifelse(dat2=='success','success','failure'))

table(sampleDatAll2$dat1, sampleDatAll2$dat2, exclude = NULL)
table(sampleDatAll2$time_to_detection, sampleDatAll2$status, exclude = NULL)

ggplot(data=sampleDatAll2) + theme_bw() +
  geom_point(aes(x= as.factor(round(time_to_detection,0)), y=value,col=as.factor(status)))+ facet_wrap(~name, scales="free")+
  labs(x="time to detection",col="status", caption="100 samples per time to detection")
  

sampleDatAll_long <- sampleDatAll  %>% pivot_longer(cols=-c(d_Sym, scen_num)) %>% mutate(dat1="all")
sampleDat_long <- sampleDat %>% pivot_longer(cols=-c(d_Sym, scen_num))  %>% mutate(dat2="success")
sampleDatAll2 <- left_join(sampleDatAll_long, sampleDat_long, by=c("scen_num", "d_Sym", "name",'value'))  %>% 
  mutate(dat2=ifelse(is.na(dat2),"no",dat2) ,status=ifelse(dat2=='success','success','failure'))

ggplot(data=sampleDatAll2) + theme_bw() +
  geom_point(aes(x=round(d_Sym,3), y=value,col=as.factor(status)))+ facet_wrap(~name, scales="free")+
  labs(x="d_Sym",col="status", caption="100 samples per time to detection")


sampleDatAll2 %>% filter(status=="success") %>% 
  group_by(time_to_detection, name) %>% 
  summarize(value =mean(value)) %>% 
  pivot_wider(names_from = name, value_from=value)



