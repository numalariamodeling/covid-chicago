# =============================================================0
# Code adapted from:  https://rpubs.com/Daniella09/108550
# =============================================================0
## Using same terminology as in https://idmod.org/docs/cms/model-file.html#function-list


rm(list = ls())
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
