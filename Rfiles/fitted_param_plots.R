
library(tidyverse)

f_plot_param <- function(exp_name, paramname, emsname, timeVarying = TRUE, SAVE = TRUE) {
  trajectoriesDat <- read.csv(file.path(simulation_output, exp_name, "trajectoriesDat.csv"))

  ### Note use Ki_EMS-  or Ki_EMS.   not Ki_EMS_  (time varying vs input parameter)
  colnames(trajectoriesDat) <- gsub("[.]", "-", colnames(trajectoriesDat))
  paramvars <- paste0(paramname, emsname, c(1:11))
  keepvars <- c("time", "startdate", paramvars)

  ### Wide to long format and calculate date
  ### And aggregate samples

  if (timeVarying == FALSE) {
    pplot <- trajectoriesDat %>%
      select(keepvars) %>%
      mutate(date = as.Date(startdate) + time) %>%
      pivot_longer(cols = -c("time", "date", "startdate"), names_to = "region") %>%
      mutate(
        region = gsub(emsname, "", gsub(paramname, "", region)),
        region = as.numeric(region),
        exp_name = exp_name,
      ) %>%
      group_by(date, region,exp_name) %>%
      summarize(value = mean(value)) %>%
      filter(date >= as.Date("2020-08-01") & date <= as.Date("2020-08-02")) %>%
      ggplot() +
      theme_cowplot() +
      geom_bar(aes(x = as.factor(region), y = value, group = region), stat = "identity", size = 1.3, position = "dodge") +
      scale_color_viridis(discrete = TRUE) +
      labs(
        y = paramname,
        title = exp_name,
        subtitle = "",
        x = "region"
      ) +
      customThemeNoFacet +
      scale_y_continuous(expand = c(0, 0)) 
  }
  if (timeVarying == TRUE) {
    pplot <- trajectoriesDat %>%
      select(keepvars) %>%
      mutate(date = as.Date(startdate) + time) %>%
      pivot_longer(cols = -c("time", "date", "startdate"), names_to = "region") %>%
      mutate(
        region = gsub(emsname, "", gsub(paramname, "", region)),
        region = as.numeric(region),
        exp_name = exp_name,
      ) %>%
      group_by(date, region,exp_name) %>%
      summarize(value = mean(value)) %>%
      filter(date <= as.Date("2020-08-02")) %>%
      ggplot() +
      theme_cowplot() +
      geom_bar(aes(x = date, y = value, col = region, group = region), stat = "identity", size = 1.3, position = "dodge") +
      scale_color_viridis(discrete = TRUE) +
      labs(
        y = paramname,
        title = exp_name,
        subtitle = "",
        x = "date"
      ) +
      customThemeNoFacet +
      scale_y_continuous(expand = c(0, 0))
  }

  if (SAVE) {
    ggsave(paste0(paramname, ".png"),
      plot = pplot, path = file.path(simulation_output, exp_name), width = 10, height = 5, device = "png"
    )
  }


  return(pplot)
}


### Load trajectories Dat
exp_name <- "20200722_IL_EMS_scen3"
#exp_name <- "20200729_IL_RR_baseline_0"


f_plot_param(exp_name = exp_name, paramname =  "backtonormal_multiplier_1_", emsname="EMS_", timeVarying = FALSE)

f_plot_param(exp_name = exp_name, paramname = "Ki_", emsname = "EMS-", timeVarying = TRUE)


