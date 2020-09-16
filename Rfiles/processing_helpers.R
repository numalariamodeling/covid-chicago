# source("load_paths.R")
library(dplyr)

## Define functions

### Load data
f_loadData <- function(data_path, simdate ='200915') {
  emresource <- read.csv(file.path(data_path, "covid_IDPH/Corona virus reports/emresource_by_region.csv")) %>%
    dplyr::mutate(
      date_of_extract = as.Date(date_of_extract),
      suspected_and_confirmed_covid_icu = suspected_covid_icu + confirmed_covid_icu
    ) %>%
    dplyr::rename(
      Date = date_of_extract,
      region = covid_region,
    ) %>%
    f_addRestoreRegion() %>%
    mutate(restore_region = tolower(restore_region)) %>%
    filter(!is.na(restore_region)) %>%
    dplyr::select(
      Date, restore_region, region, suspected_and_confirmed_covid_icu,
      confirmed_covid_deaths_prev_24h, confirmed_covid_icu, covid_non_icu
    )


  ref_df <- read.csv(file.path(data_path, "covid_IDPH/Cleaned Data", paste0(simdate, "_jg_aggregated_covidregion.csv")))

  ref_df <- ref_df %>%
    dplyr::rename(
      Date = date,
      region = covid_region,
      LL_deaths = deaths,
      LL_cases = cases,
      LL_admissions = admissions
    ) %>%
    f_addRestoreRegion() %>%
    mutate(restore_region = tolower(restore_region))


  ref_df$Date <- as.Date(ref_df$Date)
  emresource$Date <- as.Date(emresource$Date)


  out <- left_join(emresource, ref_df, by = c("Date", "restore_region", "region"))

  return(out)
}




regions <- list(
  "Northcentral" = c(1, 2),
  "Northeast" = c(7, 8, 9, 10, 11),
  "Central" = c(3, 6),
  "Southern" = c(4, 5),
  "Illinois" = c(1:11)
)

f_addRestoreRegion <- function(dat) {
  dat$restore_region <- NA
  dat$restore_region[dat$region %in% regions$Northcentral] <- "Northcentral"
  dat$restore_region[dat$region %in% regions$Northeast] <- "Northeast"
  dat$restore_region[dat$region %in% regions$Central] <- "Central"
  dat$restore_region[dat$region %in% regions$Southern] <- "Southern"


  return(dat)
}

combineDat <- function(filelist, namelist) {
  count <- 0
  for (i in c(1:length(filelist))) {
    count <- count + 1
    dat <- read_csv(file.path(filelist[i]))
    dat$exp_name <- namelist[i]
    if (count == 1) combinedDat <- dat
    if (count >= 1) combinedDat <- rbind(combinedDat, dat)
  }
  return(combinedDat)
}


load_population <- function(){
  geography_name <- c('illinois',c(1:11))
  pop <- c("12830632", "688393","1269519","581432",'676017','424810','760362','791009','1432193','1012222','2477754','2716921')
  df <-as.data.frame( cbind(geography_name, pop))
  
  perRR=F
  if(perRR){
    popdat <- load_population() %>% 
      mutate(region =as.character(geography_name) ) %>% 
      filter(region !="illinois") %>%
      f_addRestoreRegion() %>% 
      group_by(restore_region) %>%
      summarize(pop=sum(as.numeric(pop))) %>%
      mutate(geography_name = tolower(restore_region))
    
  }
  return(df)
}


load_new_capacity <- function(selected_ems = NULL, simdate = "20200915") {


  fname <- paste0("capacity_weekday_average_",simdate,".csv")
  df <- read.csv(file.path(data_path, "covid_IDPH/Corona virus reports/hospital_capacity_thresholds_template", fname))


  df <- df %>%
    filter(overflow_threshold_percent == 1) %>%
    select(geography_modeled, resource_type, avg_resource_available_prev2weeks) %>%
    unique() %>%
    pivot_wider(names_from = "resource_type", values_from = "avg_resource_available_prev2weeks") %>%
    mutate(geography_name = gsub("covidregion_", "", geography_modeled)) %>%
    select(geography_name, icu_availforcovid, hb_availforcovid)

  dfRR <- df %>%
    rename(region = geography_name) %>%
    f_addRestoreRegion() %>%
    group_by(restore_region) %>%
    summarize(
      icu_availforcovid = sum(icu_availforcovid),
      hb_availforcovid = sum(hb_availforcovid)
    ) %>%
    mutate(geography_name = tolower(restore_region)) %>%
    select(geography_name, icu_availforcovid, hb_availforcovid)

  dfIL <- df %>%
    summarize(
      icu_availforcovid = sum(icu_availforcovid),
      hb_availforcovid = sum(hb_availforcovid)
    ) %>%
    mutate(geography_name = "illinois") %>%
    select(geography_name, icu_availforcovid, hb_availforcovid)


  df <- rbind(df, dfRR, dfIL) %>%
    as.data.frame() %>%
    rename(
      icu_available = icu_availforcovid,
      medsurg_available = hb_availforcovid
    )

  if (!(is.null(selected_ems))) df <- df %>% filter(geography_name %in% selected_ems)

  return(df)
}


load_capacity <- function(selected_ems = NULL) {
  df <- read.csv(file.path(data_path, "covid_IDPH/Corona virus reports/capacity_by_covid_region.csv"))

  ## Take mean of last 2 weeks
  filterDate <- max(as.Date(df$date)) - 14

  df <- df %>%
    filter(date == filterDate & geography_name != "chicago") %>%
    mutate(
      geography_name = gsub("restore_", "", geography_name),
      medsurg_available = medsurg_total - medsurg_noncovid,
      icu_available = icu_total - icu_noncovid,
      vents_available = vent_total - vent_noncovid
    ) %>%
    group_by(geography_name) %>%
    summarize(
      icu_available = mean(icu_available),
      medsurg_available = mean(medsurg_available),
      vents_available = mean(vents_available)
    )

  if (!(is.null(selected_ems))) df <- df %>% filter(geography_name %in% selected_ems)

  return(df)
}


customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 12, face = "bold"),
  strip.text.y = element_text(size = 12, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 16, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 12),
  plot.caption = element_text(size = 8),
  legend.title = element_text(size = 12),
  legend.text = element_text(size = 12),
  axis.title.x = element_text(size = 12),
  axis.text.x = element_text(size = 12),
  axis.title.y = element_text(size = 12),
  axis.text.y = element_text(size = 12)
)

## Extended and edited from:
# https://stackoverflow.com/questions/35953394/calculating-length-of-95-ci-using-dplyr

# library(dplyr)

## Custom functions
## To Do: add multiple variables at once ?

f_aggrDat <- function(dataframe, groupVars, valueVar, WideToLong = FALSE) {
  # dataframe = dataframe to aggregate (new datafram will be created)
  # groupVars = variables to aggregate at
  # valueVar = variable to aggregate
  # WideToLong = transfrom data to long format,
  #              so that statistics are in one column instead of spread over rows
  dataframe <- as.data.frame(dataframe)
  dataframe$tempvar <- dataframe[, colnames(dataframe) == valueVar]
  datAggr <- dataframe %>%
    dplyr::group_by_(.dots = groupVars) %>%
    dplyr::summarise(
      min.val = min(tempvar, na.rm = TRUE),
      max.val = max(tempvar, na.rm = TRUE),
      mean.val = mean(tempvar, na.rm = TRUE),
      median.val = median(tempvar, na.rm = TRUE),
      sd.val = sd(tempvar, na.rm = TRUE),
      n.val = n(),
      q25 = quantile(tempvar, probs = 0.25, na.rm = TRUE),
      q75 = quantile(tempvar, probs = 0.75, na.rm = TRUE),
      q2.5 = quantile(tempvar, probs = 0.025, na.rm = TRUE),
      q97.5 = quantile(tempvar, probs = 0.975, na.rm = TRUE)
    ) %>%
    dplyr::mutate(
      se.val = sd.val / sqrt(n.val),
      lower.ci.val = mean.val - qt(1 - (0.05 / 2), n.val - 1) * se.val,
      upper.ci.val = mean.val + qt(1 - (0.05 / 2), n.val - 1) * se.val,
      weighted = 0
    ) %>%
    # dplyr::select(-sd.val, -n.val,-se.val) %>%
    as.data.frame()

  if (WideToLong) {
    datAggr <- gather(datAggr, -groupVars)
    colnames(datAggr)[colnames(datAggr) == "variable"] <- "statistic"
    colnames(datAggr)[colnames(datAggr) == "value"] <- valueVar
    datAggr$statistic <- gsub(".val", "", datAggr$statistic)
  }

  return(datAggr)
}

## keep both names as long as not all scripts are updated
aggrDat <- f_aggrDat

f_weighted.aggrDat <- function(dataframe, groupVars, valueVar, weightVar, WideToLong = FALSE) {
  # dataframe = dataframe to aggregate (new datafram will be created)
  # groupVars = variables to aggregate at
  # valueVar = variable to aggregate
  # WideToLong = transfrom data to long format,
  #              so that statistics are in one column instead of spread over rows

  dataframe <- as.data.frame(dataframe)
  dataframe$tempvar <- dataframe[, colnames(dataframe) == valueVar]
  dataframe$w <- dataframe[, colnames(dataframe) == weightVar]

  datAggr <- dataframe %>%
    dplyr::group_by_(.dots = groupVars) %>%
    dplyr::summarise(
      min.val = min(tempvar, na.rm = TRUE),
      max.val = max(tempvar, na.rm = TRUE),
      mean.val = weighted.mean(tempvar, w),
      median.val = weighted.median(tempvar, w),
      sd.val = sqrt(sum(w * (tempvar - mean.val)^2)),
      n.val = n(),
      q25 = weighted.quantile(tempvar, w, probs = 0.25),
      q75 = weighted.quantile(tempvar, w, probs = 0.75),
      q2.5 = weighted.quantile(tempvar, w, probs = 0.025),
      q97.5 = weighted.quantile(tempvar, w, probs = 0.975)
    ) %>%
    dplyr::mutate(
      se.val = sd.val / sqrt(n.val),
      lower.ci.val = mean.val - qt(1 - (0.05 / 2), n.val - 1) * se.val,
      upper.ci.val = mean.val + qt(1 - (0.05 / 2), n.val - 1) * se.val,
      weighted = 1
    ) %>%
    # dplyr::select(-sd.val, -n.val,-se.val) %>%
    as.data.frame()

  if (WideToLong) {
    datAggr <- gather(datAggr, -groupVars)
    colnames(datAggr)[colnames(datAggr) == "variable"] <- "statistic"
    colnames(datAggr)[colnames(datAggr) == "value"] <- valueVar
    datAggr$statistic <- gsub(".val", "", datAggr$statistic)
  }

  return(datAggr)
}
