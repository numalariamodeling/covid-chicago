### R script to calculate relative increase in tests done over time in Illinous
### The values will be used as scaling factor for the detection rates in the SEIR model

require(tidyverse)
require(cowplot)

username <- Sys.getenv("USERNAME")

if (username == "mrung") {
  wdir <- file.path("C:/Users", username, "Box/NU-malaria-team/data/covid_chicago/")
  input_dir <- file.path("C:/Users", username, "gitrepos/covid-chicago/snippets/")
}

## ==================================================
### Detection dates in emodl will depend on start date of the simulation
startDate_testing <- as.Date("2020-03-04")
startDate_emodl <- as.Date("2020-02-20")
offset <- startDate_testing - startDate_emodl
## ==================================================


IL_testing <- read_csv(file.path(wdir, "IL_testing.csv"), skip = 1)
IL_testing$rownum <- rev(c(1:nrow(IL_testing)))
IL_testing <- IL_testing %>% arrange(rownum)
IL_testing$Date_adj <- seq(as.Date("2020-03-04"), as.Date("2020-03-04") + nrow(IL_testing) - 1, by = "day")

totalTests_All <- max(IL_testing$Positive + IL_testing$Negative)

### Calculate additional variables

IL_testing <- IL_testing %>%
  # separate(Date, into = c("Weekday","Month","Day","Year"), sep=" ") %>%
  mutate(
    total_tested = Positive + Negative,
    new_tested = total_tested - lag(total_tested, default = total_tested[1]),
    rel_incr_new = new_tested / sum(new_tested),
    rel_incr_total = total_tested / totalTests_All,
    TPR = Positive / total_tested,
    emodlDay = rownum + offset
  )


showPlot <- F
if (showPlot) {
  #### Descriptive
  customcols <- c("relative increase\n in cumulative testing" = "black", "TPR" = "orange")
  ggplot(data = IL_testing) + theme_cowplot() +
    geom_line(aes(x = Date_adj, y = rel_incr_total, col = "relative increase\n in cumulative testing", group = 1), size = 1.3) +
    geom_line(aes(x = Date_adj, y = TPR, col = "TPR", group = 1), size = 1.3) +
    scale_color_manual(values = customcols) +
    labs(y = "", x = "", col = "", title = "Illinois testing data", subtitle = "total tests n=75'066")

  ggplot(data = IL_testing) + theme_cowplot() +
    geom_bar(aes(x = Date_adj, y = total_tested), stat = "identity") +
    labs(y = "", x = "Time", col = "", title = "Illinois testing data\n")

  customcols <- c("relative increase\n in new tests" = "grey", "relative increase\n in cumulative testing" = "black")
  ggplot(data = IL_testing) + theme_cowplot() +
    geom_line(aes(x = Date_adj, y = rel_incr_total, col = "relative increase\n in cumulative testing", group = 1), size = 1.3) +
    geom_line(aes(x = Date_adj, y = rel_incr_new, col = "relative increase\n in new tests", group = 1), size = 1.3) +
    scale_color_manual(values = customcols) +
    labs(y = "", x = "", col = "", title = "Illinois testing data", subtitle = paste0("total tests n=", totalTests_All))
}

## =========================================================
## Write increase in detection snippet
## =========================================================

txtdat <- IL_testing[, c("Date_adj", "rownum", "rel_incr_total", "emodlDay")]
txtdat <- txtdat %>% arrange(rownum)
txtdat

sink(file.path(input_dir, "emodl_detection_snippet.txt"))
cat(paste0("
(time-event detection @detection_time_", txtdat$rownum, "@ ((d_As d_As_incr", txtdat$rownum, ") (d_Sym d_Sym_incr", txtdat$rownum, ") (d_Sys d_Sys_incr", txtdat$rownum, "))) "))
cat(paste0("\n(param d_As_incr", txtdat$rownum, " (* d_As @detection_multiplier_", txtdat$rownum, "@))\n(param d_Sym_incr", txtdat$rownum, " (* d_Sym @detection_multiplier_", txtdat$rownum, "@))\n(param d_Sys_incr", txtdat$rownum, " (* d_As @detection_multiplier_", txtdat$rownum, "@))"))
sink()


sink(file.path(input_dir, "param_detection_snippet.txt"))
cat(paste0("\ndf['detection_multiplier_", txtdat$rownum, "'] = np.random.uniform(", txtdat$rel_incr_total, ",", txtdat$rel_incr_total, ", samples)"))
cat(paste0("\ndf['detection_time_", txtdat$rownum, "'] = ", txtdat$emodlDay, ""))
sink()


sink(file.path(input_dir, "param_replace_snippet.txt"))
cat(paste0("\ndata = data.replace('@detection_multiplier_", txtdat$rownum, "@', str(df.detection_multiplier_", txtdat$rownum, "[sample_nr]))"))
cat(paste0("\ndata = data.replace('@detection_time_", txtdat$rownum, "@', str(df.detection_time_", txtdat$rownum, "[sample_nr]))"))
sink()
