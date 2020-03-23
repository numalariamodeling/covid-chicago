# =============================================================0
# Code adapted from:  https://rpubs.com/Daniella09/108550
# =============================================================0
## Using same terminology as in https://idmod.org/docs/cms/model-file.html#function-list

library(tidyverse)
library(cowplot)
library(cowplot)
library(deSolve)


#rm(list = ls())
# contact_rate = 27                     
# transmission_probability = 0.18       
recovery_rate <- 16 
incubation_period <- 6.63
waning <- 180


Ki <- 0.0009 # contact_rate * transmission_probability
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
      dS <- (-Ki * S * I) + (Kw * R)
      dE <- (Ki * S * I) - (Kl * E)
      dI <- (Kl * E) - (Kr * I)
      dR <- (Kr * I) - (Kw * R)

      results <- c(dS, dE, dI, dR)
      list(results)
    }
  )
}


# Initial state values 
initial_values <- c(S = 990, E = 0, I = 10, R = 0)
N <- sum(initial_values)
timepoints <- seq(0, 30, by = 1)

modelResults <- as.data.frame(lsoda(initial_values, timepoints, seir_model, parameter_list))

# Plot dynamics of Susceptibles sub-population.
matplot(modelResults$time, modelResults[, 2:5],
  type = "l", xlab = "time in days", ylab = "Human Population",
  main = "Human", lwd = 2
)
legend("topright", xpd = TRUE, bty = "n", horiz = TRUE, inset = c(0, 0), c("S", "E", "I", "R"), col = 1:4, lty = 1:4)
# pdf(file="plot_human.pdf")   # save as pdf



##### COmpare with data 
illinois_pop = 12671821
pred = modelResults %>%  
        pivot_longer(-time,names_to = "outcome") %>% 
        mutate(dat="pred",
               value = value/1000* illinois_pop )

        
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

ggplot(data=subset(combinedDat, outcome!="S")) + geom_line(aes(x=time, y=value, col=outcome, linetype=dat))
