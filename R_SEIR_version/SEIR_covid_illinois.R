### ==========================================
### Project: Covid-19 Chicago
### MR
### Setting: ILLINOIS
### Input:
### - Daily confirmed cases - cumulative for Illinois
###
### Output:
### Plot with cumulative confirmed cases and deaths in illinois
### ==========================================
### Code adapted from:  https://rpubs.com/Daniella09/108550
### =============================================================
### Using same terminology as in https://idmod.org/docs/cms/model-file.html#function-list
### =============================================================

library(tidyverse)
library(cowplot)
library(scales)
library(deSolve)

username <- Sys.getenv("USERNAME")
project_dir <- file.path("C:/Users/", username, "/Box/NU-malaria-team/projects/covid_chicago")

#### Model parameters (partly per setting, partly default)
total_pop <- 12671821
inInfect <- 12
recovery_rate <- 16
incubation_period <- 6.63
waning <- 180
Ki <- 0.00000019

initial_values <- c(S = total_pop - inInfect, E = 0, I = inInfect, R = 0)

Kr <- 1 / recovery_rate
Kl <- 1 / incubation_period
Kw <- 1 / waning

parameter_list <- c(Ki = Ki, Kr = Kr, Kw = Kw)

# Compute Ro - Reproductive number.
(Ro <- Ki / Kr)

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
plot <- F
if (plot) {
  matplot(modelResults$time, modelResults[, 2:5],
    type = "l", xlab = "time in days", ylab = "Human Population",
    main = "Human", lwd = 2
  )
  legend("topright", xpd = TRUE, bty = "n", horiz = TRUE, inset = c(0, 0), c("S", "E", "I", "R"), col = 1:4, lty = 1:4)
  # pdf(file="plot_human.pdf")   # save as pdf
}


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

modelResults["time_hospitalized"] <- modelResults["time"] + time_to_hospitalization
modelResults["time_critical"] <- modelResults["time_hospitalized"] + time_to_critical
modelResults["time_death"] <- modelResults["time_critical"] + time_to_death

modelResults["symptomatic"] <- modelResults["I"] * fraction_symptomatic
modelResults["hospitalized"] <- modelResults["symptomatic"] * fraction_hospitalized
modelResults["critical"] <- modelResults["hospitalized"] * fraction_critical
modelResults["deaths"] <- modelResults["critical"] * fraction_death


##### Compare with data
pred <- modelResults %>%
  mutate(I_H = I + hospitalized) %>%
  pivot_longer(-time, names_to = "outcome") %>%
  mutate(dat = "pred") # %>%
# mutate(value = value/1000* illinois_pop )

#### Load data
datD <- read.csv(file.path(project_dir, "Illinois_data/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"))
datC <- read.csv(file.path(project_dir, "Illinois_data/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"))

editDat <- function(dat) {
  colnames(dat) <- gsub("*X", "date_", colnames(dat))

  dat <- dat %>%
    pivot_longer(cols = -c(Province.State, Country.Region, Lat, Long), names_to = "Date") %>%
    separate(Date, into = c("del", "Date"), sep = "_") %>%
    select(-del) %>%
    mutate(Date = as.Date(Date, format = "%m.%d.%y")) %>%
    group_by(Province.State, Country.Region) %>%
    arrange(Province.State, Country.Region, Date) %>%
    mutate(nday = dplyr::row_number()) %>%
    as.data.frame()

  return(dat)
}

datD <- editDat(datD)
datC <- editDat(datC)

datD$outcome <- "deaths"
datC$outcome <- "confirmed cases"

dat <- rbind(datD, datC) %>% as.data.frame()

illinois <- as.data.frame(dat[grep("Illinois", dat$Province.State), ])

### Requires additonal update data for 2020-03-23, based on http://www.dph.illinois.gov/
illinois$value[illinois$Date == "2020-03-23" & illinois$outcome == "confirmed cases"] <- 1285
illinois$value[illinois$Date == "2020-03-23" & illinois$outcome == "deaths"] <- 12


dat <- illinois %>%
  mutate(time = nday - 48, dat = "data") %>%
  filter(nday >= 48) %>%
  select(time, outcome, value, dat)

combinedDat <- rbind(dat, pred)


### Prepare custom plot
customPlot <- function(OUTCOMES, ymax, TITLE) {
  ## OUTCOMES = c("confirmed cases","I","E","hospitalized")
  ## ymax = 95000
  ## TITLE = 'confirmed cases, and predicted exposed, infectious and hospitalized'
  pout <- ggplot(data = subset(combinedDat, (outcome %in% OUTCOMES))) +
    geom_line(aes(x = time, y = value, col = outcome, linetype = dat), size = 1.3) +
    geom_point(
      data = subset(combinedDat, (outcome %in% OUTCOMES) & dat == "data"),
      aes(x = time, y = value, col = outcome), shape = 21, fill = "white", size = 3
    ) +
    scale_x_continuous(lim = c(0, 17), breaks = seq(0, 17, 1), labels = seq(0, 17, 1)) +
    scale_y_continuous(lim = c(0, ymax)) +
    labs(
      title = TITLE, y = "Population (n)",
      x = ""
    ) +
    theme_bw()
  
  return(pout)
}


## Deaths over time
p1 <- customPlot(OUTCOME=c("deaths"), ymax= 20, TITLE="")
ggplot(data = subset(combinedDat, (outcome %in% c("deaths")))) 


p2a <- customPlot(
  OUTCOME = c("confirmed cases", "I", "E", "hospitalized"), ymax = 95000,
  TITLE = "confirmed cases, and predicted exposed, infectious and hospitalized"
)

p2b <- customPlot(
  OUTCOME = c("confirmed cases", "I", "hospitalized"), ymax = 31000,
  TITLE = "confirmed cases, and predicted infectious and hospitalized"
) +
  theme(legend.position = "none", panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank())


p2c <- customPlot(
  OUTCOME = c("confirmed cases", "hospitalized"), ymax = 7000,
  TITLE = "confirmed cases, and predicted hospitalized"
) +
  labs(x = "Time since first reported cases on 2020-03-10") +
  theme(legend.position = "none", panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank())


## Extract legend
legend <- get_legend(p2a)
p2a <- p2a + theme(legend.position = "none")

pplot <- plot_grid(p2a, p2b, p2c, ncol = 1)
pplot2 <- plot_grid(pplot, legend, ncol = 2, rel_widths = c(1, 0.3))

ggsave("sample_plot_illinpis.png",
  plot = pplot2, device = "png", path = file.path(projectDir, "r_sim"),
  width = 10, height = 12
)
