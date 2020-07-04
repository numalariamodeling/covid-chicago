
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



simdir <- file.path(simulation_output, "MR_tests/state_event/")



##################################################
dat1 <- read.csv(file.path(simdir,"20200619_EMS_11_state_eventTest3/trajectoriesDat.csv"))

dat1 <- dat1 %>% mutate(Date = time + as.Date(startdate))

ggplot(data=subset(dat1, d_AsP_ct1 ==0.5)) + 
  theme_cowplot() +  customThemeNoFacet +
  geom_line(aes(x=Date, y=d_Sym_t),size=2) + 
  facet_wrap(~d_Sym_ct1)+
  labs(subtitle="d_Sym_ct1") +
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf)) 


tempdat = subset(dat1, d_AsP_ct1 ==0.5 & infected < 1)
tempdat <- tempdat %>% group_by(d_Sym_ct1) %>% mutate(dateDiff = as.numeric( min(Date) - as.Date("2020-06-01")) )

table(tempdat$dateDiff, tempdat$d_Sym_ct1)

ggplot() + 
  theme_cowplot() +  customThemeNoFacet +
  geom_line(data=subset(dat1, d_AsP_ct1 ==0.5 & Date >= "2020-06-01"), aes(x=Date, y=infected),size=2) + 
  geom_line(data=subset(dat1, d_AsP_ct1 ==0.5 & infected < 1), aes(x=Date, y=infected),col = "red", size=3) + 
  facet_wrap(~d_Sym_ct1)+
  labs(subtitle="d_Sym_ct1") +
  #geom_hline(yintercept = 1,col="red", size=1.5, linetype="dashed") +   
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf)) +
  scale_y_log10()
  

ggplot(data=dat1) +
  theme_cowplot() +  customThemeNoFacet +
  geom_line(aes(x=Date, y=infected, col=as.factor(d_Sym_ct1)),size=2) +
  facet_wrap(~d_AsP_ct1)+
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf)) 

##################################################
dat0 <- read.csv(file.path(simdir, "20200619_TEST_generic_test/trajectoriesDat.csv"))
dat <- dat0 

dat <- dat %>% mutate(Date = time + as.Date(startdate)) %>% filter(Ki!=0)

ggplot(data=subset(dat, time <100)) +
  theme_cowplot() +  customThemeNoFacet +
  geom_line(aes(x=Date, y=susceptible),size=2) +
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf)) +
  facet_wrap(~ Ki, scales="free")
##################################################


stateEventTrigger <- c("critical","C3_det3","critical_dead","detected","infected","none")

nexpsfiles <- list.files(file.path(simdir , "simplemodel"), pattern = "trajectoriesDat" , recursive = TRUE, full.names = TRUE)[1]
#nexpsfiles <- list.files(file.path(simdir , "emsmodel"), pattern = "trajectoriesDat" , recursive = TRUE, full.names = TRUE)

tdat <- trajectoriesDat <- sapply(file.path(nexpsfiles), read.csv, simplify = FALSE) %>%
  bind_rows(.id = "id") %>%
  as.data.frame() %>%
  mutate(Date = time + as.Date(startdate))


tdat$id <- gsub(simdir, "",tdat$id)
tdat$id <- gsub("/emsmodel/", "",tdat$id)
tdat$id <- gsub("/simplemodel/", "",tdat$id)
tdat$id <- gsub("/trajectoriesDat.csv", "",tdat$id)
tdat$id <- gsub("20200619_EMS_11_state_", "",tdat$id)
tdat$id <- gsub("20200619_TEST_state_", "",tdat$id)

table(tdat$id)
table(tdat$reduced_inf_of_det_cases_ct1)
table(tdat$d_AsP_ct1)
table(tdat$d_Sym_ct1)
table(tdat$reduce_testDelay_Sym_1)



ggplot(data=subset(tdat, Date <= "2020-12-30" )) + 
  theme_cowplot() +  customThemeNoFacet +
  geom_line(aes(x=Date, y=d_Sym_t, col=as.factor(d_Sym_ct1),group=interaction(scen_num, d_Sym_ct1)),size=1.3) + 
  facet_wrap(~ id) + 
  labs(subtitle="") +
  labs(color="CT detection rate of Sym")+
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf)) +
  scale_color_viridis(discrete = TRUE, direction = -1)

tdat <- tdat %>% filter(id=="infected")

ggplot(data=subset(tdat )) + 
  theme_cowplot() +  customThemeNoFacet +
  geom_line(aes(x=Date, y=critical, col=as.factor(d_Sym_ct1),group=interaction(scen_num, d_Sym_ct1)),size=1.3) + 
  facet_wrap(~ id) + 
  labs(color="CT detection rate of Sym")+
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf)) +
  scale_color_viridis(discrete = TRUE, direction = -1)


ggplot(data=subset(tdat , Date >= "2020-06-01" & Date <= "2020-12-01")) + 
  theme_cowplot() +  customThemeNoFacet +
  geom_line(aes(x=Date, y=critical, col=as.factor(d_Sym_ct1),group=interaction(scen_num, d_Sym_ct1)),size=1.3) + 
  facet_wrap(~ id) + 
  labs(color="CT detection rate of Sym")+
  geom_hline(yintercept = c(-Inf, Inf)) +   
  geom_vline(xintercept = c(-Inf, Inf))  +
  scale_color_viridis(discrete = TRUE, direction = -1)+
  scale_x_date(date_breaks = "2 week", date_labels = "%B")+
  facet_grid( reduce_testDelay_Sym_1~d_AsP_ct1 )


minc <- tdat %>% filter(Date>= "2020-06-01" & C3_det3 <1 & id =="C3_det3")
ggplot(data=minc, aes(x=Date, y=d_Sym_t)) +geom_point()
