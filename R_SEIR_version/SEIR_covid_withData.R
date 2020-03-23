# =============================================================0
# Code adapted from:  https://rpubs.com/Daniella09/108550
# =============================================================0
## Using same terminology as in https://idmod.org/docs/cms/model-file.html#function-list

library(tidyverse)
library(cowplot)
library(cowplot)
library(deSolve)

illinois_pop = 12671821
initial_values <- c(S = illinois_pop-12, E = 0, I = 12, R = 0)
#initial_values <- c(S = 988, E = 0, I = 12, R = 0)

#rm(list = ls())
# contact_rate = ?                      
# transmission_probability = 0.18       
recovery_rate <- 16 
incubation_period <- 6.63
waning <- 180


Ki <- 0.00000019 # contact_rate * transmission_probability
Kr <- 1 / recovery_rate
Kl <- 1 / incubation_period
Kw <- 1 / waning

parameter_list <- c(Ki = Ki, Kr = Kr, Kw = Kw)

# Compute Ro - Reproductive number.
Ro <- Ki / Kr

seir_model <- function(current_timepoint, state_values, parameters) {
  # create state variables (local variables)
  S <- state_values [1] # susceptibles
  E <- state_values [2] # exposed
  I <- state_values [3] # infectious
  R <- state_values [4] # recovered

  with(
    as.list(parameters),
    {
      dS <- (-Ki * I) + (Kw * R)
      dE <- (Ki * S * I) - (Kl * E)
      dI <- (Kl * E) - (Kr * I)
      dR <- (Kr * I) - (Kw * R)

      results <- c(dS, dE, dI, dR)
      list(results)
    }
  )
}


# Initial state values 
N <- sum(initial_values)
timepoints <- seq(0, 30, by = 1)

modelResults <- as.data.frame(lsoda(initial_values, timepoints, seir_model, parameter_list))

# Plot dynamics of Susceptibles sub-population.
plot=F
if(plot){
matplot(modelResults$time, modelResults[, 2:5],
  type = "l", xlab = "time in days", ylab = "Human Population",
  main = "Human", lwd = 2
)
legend("topright", xpd = TRUE, bty = "n", horiz = TRUE, inset = c(0, 0), c("S", "E", "I", "R"), col = 1:4, lty = 1:4)
# pdf(file="plot_human.pdf")   # save as pdf
}


#### Calculate additional outcomes
##### Hospitaliszations and deaths (from python script, to do: add sample num)
CFR <- 0.016
fraction_symptomatic <- 0.7
fraction_hospitalized <- 0.3
fraction_critical <- 0.8
time_to_hospitalization <- 6
time_to_critical <- 6
time_to_death <- 2

fraction_death <- CFR / (fraction_hospitalized * fraction_critical)

modelResults["time_hospitalized"] <- modelResults["time"] + time_to_hospitalization
modelResults["time_critical"] <- modelResults["time_hospitalized"] + time_to_critical
modelResults["time_death"] <- modelResults["time_critical"] + time_to_death

modelResults["symptomatic"] <- modelResults["I"] * fraction_symptomatic
modelResults["hospitalized"] <- modelResults["symptomatic"] * fraction_hospitalized
modelResults["critical"] <- modelResults["hospitalized"] * fraction_critical
modelResults["deaths"] <- modelResults["critical"] * fraction_death




##### Compare with data 
pred = modelResults %>%  mutate(I_H = I+hospitalized) %>% 
        pivot_longer(-time,names_to = "outcome") %>% 
        mutate(dat="pred") #%>% 
       #mutate(value = value/1000* illinois_pop )

        
datD <- read.csv("C:/Users/mrung/gitrepos/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv")
datC<- read.csv("C:/Users/mrung/gitrepos/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv")

editDat <- function(dat){
  colnames(dat ) <- gsub("*X","date_",colnames(dat ))
  
  dat <- dat %>% pivot_longer(cols=-c(Province.State ,Country.Region  ,   Lat  ,   Long), names_to = "Date") %>%
    separate(Date, into=c("del","Date"), sep="_") %>% select(-del) %>%
    mutate(Date = as.Date(Date, format="%m.%d.%y")) %>% 
    group_by(Province.State ,Country.Region) %>% 
    arrange(Province.State ,Country.Region,Date) %>%
    mutate(nday = dplyr::row_number()) %>%
    as.data.frame()
  
  return(dat)
}

datD <- editDat(datD)
datC <- editDat(datC)

datD$outcome="deaths"
datC$outcome="confirmed cases"

dat <- rbind(datD,datC) %>% as.data.frame

illinois <- as.data.frame(dat[grep("Illinois",dat$Province.State),])
dat <- illinois %>% 
        mutate(time=nday-48,dat="data") %>% filter(nday>=48) %>%
        select(time, outcome, value, dat)

combinedDat <- rbind(dat, pred)



ggplot(data=subset(combinedDat, (outcome %in% c("deaths")))) + 
  geom_line(aes(x=time, y=value, col=outcome, linetype=dat),size=1.3)+
  geom_label(data=subset(combinedDat, dat=="data" & value>0 & (outcome %in% c("deaths"))),
             aes(x=time, y=value, label=value, col=outcome, linetype=dat),size=3)+
  scale_x_continuous(lim=c(0,15))+
  scale_y_continuous(lim=c(0,15))+
  labs(y="Population (n)",
       x="Time since first reported cases on 2020-03-10")+
  theme_bw()

ggplot(data=subset(combinedDat, (outcome %in% c("confirmed cases","I","hospitalized")))) + 
  geom_line(aes(x=time, y=value, col=outcome, linetype=dat),size=1.3)+
  #geom_label(data=subset(combinedDat, dat=="data" & value>0 & (outcome %in% c("confirmed cases"))),
  #           aes(x=time, y=value, label=value, col=outcome, linetype=dat),size=3)+
  scale_x_continuous(lim=c(0,15))+
  scale_y_continuous(lim=c(0,2000))+
  labs(y="Population (n)",
       x="Time since first reported cases on 2020-03-10")+
  theme_bw()
