###-----------------------------------------------------------------
###
### Define functions often used in analysis and data processing
### Many functions are specific for the spatial COVID-19 model, others are generic
### Paths are not loaded or necessarily specified in function arguments and need to be loaded via load_paths.R
###
###-----------------------------------------------------------------

customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.text.y= element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.text.y= element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)


f_loadData <- function(data_path, LL_file_date = NULL) {
  
  #' Load reference data and merge files
  #'
  #' Load reference data, EMResource and Line list data
  #' Per default adds the restore regions and selects specified variables.
  #' Output a merged dataframe in wide format.
  #' @param data_path directory path to uppr level that includes covid_IDPH , covid_chicago..
  #' @param LL_file_date date of the lates line list data
  #' 
  
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
    dplyr::mutate(restore_region = tolower(restore_region)) %>%
    dplyr::filter(!is.na(restore_region)) %>%
    dplyr::select(
      Date, restore_region, region, suspected_and_confirmed_covid_icu,
      confirmed_covid_deaths_prev_24h, confirmed_covid_icu, covid_non_icu
    )

  LLdir <- file.path(data_path, "covid_IDPH", "Cleaned Data")
  if (is.null(LL_file_date)) {
    LLfiles <- list.files(LLdir)[grep("aggregated_covidregion", list.files(LLdir))]
    LL_file_dates <- as.numeric(gsub("_jg_aggregated_covidregion.csv", "", LLfiles))
    LL_file_date <- max(LL_file_dates)
  }


  ref_df <- read.csv(file.path(LLdir, paste0(LL_file_date, "_jg_aggregated_covidregion.csv")))

  ref_df <- ref_df %>%
    dplyr::rename(
      Date = date,
      region = covid_region,
      LL_deaths = deaths,
      LL_cases = cases,
      LL_admissions = admissions
    ) %>%
    f_addRestoreRegion() %>%
    dplyr::mutate(restore_region = tolower(restore_region))


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
  
  #' Adds a restore regions grouping  variable for covid regions
  #'
  #' @param dat dataframe with region variable in numeric format (1-11)
  #' 
  
  regions <- list(
    "Northcentral" = c(1, 2),
    "Northeast" = c(7, 8, 9, 10, 11),
    "Central" = c(3, 6),
    "Southern" = c(4, 5),
    "Illinois" = c(1:11)
  )

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


f_combine_csv <- function(csv_dir, fname){
  #' Combines multiple csv files of same format and column names into one dataframe using rbind
  #'
  #' requires data.table for fast load
  #' @param csv_dir directory name that includes csv files
  #' @param fname pattern of csv file name, also used to save combined csv file
  #' 
  library(data.table)
  
  Files <- list.files(csv_dir)[grep(fname,list.files(csv_dir))]
  
  datList <- list()
  for (file in  Files ) {
    temp_csv <- fread(file.path(csv_dir, file))
    temp_csv$scen_num <- as.numeric(row.names(temp_csv))
    datList[[length(datList)+1]] <-temp_csv
    rm(temp_csv)
  }
  dat <- datList %>% bind_rows() 
  fwrite(dat, file = file.path(csv_dir, paste0(fname,"_combined.csv")), row.names = FALSE)
  return(dat)
}



load_population <- function(perRR=FALSE) {
  #' Load population estimates per covid region (hardcoded)
  #'
  #' Using same values as specified in the yaml files. 
  #' @param perRR specified whether to aggregate per restore region, default is per covid region
 library(dplyr)
  
  geography_name <- c("illinois", c(1:11))
  pop <- c("12830632", "688393", "1269519", "581432", "676017", "424810", "760362", "791009", "1432193", "1012222", "2477754", "2716921")
  df <- as.data.frame(cbind(geography_name, pop))

  if (perRR) {
    popdat <- load_population() %>%
      dplyr::mutate(region = as.character(geography_name)) %>%
      dplyr::filter(region != "illinois") %>%
      f_addRestoreRegion() %>%
      dplyr::group_by(restore_region) %>%
      dplyr::summarize(pop = sum(as.numeric(pop))) %>%
      dplyr::mutate(geography_name = tolower(restore_region))
  }
  return(df)
}


load_new_capacity <- function(selected_ems = NULL, filedate = NULL) {
  #' Load ICU and non ICU capacity estimates
  #'
  #' The csv file is weekly updated and provided by CIVIS
  #' @param selected_ems if specified, the dataframe is filtered for that region
  #' @param filedate date of csv file to use, if not specified latest file is selected
  #' 
  library(dplyr)
  
  capacity_dir <- file.path(data_path, "covid_IDPH/Corona virus reports/hospital_capacity_thresholds")

  if (is.null(filedate)) {
    files <- list.files(capacity_dir)[grep("capacity_weekday_average", list.files(capacity_dir))]
    files <- files[(nchar(files)==37)]
    dates <- as.numeric(gsub(".csv", "", gsub("capacity_weekday_average_", "", files)))
    filedate <- max(dates)
  }

  fname <- paste0("capacity_weekday_average_", filedate, ".csv")
  df <- read.csv(file.path(capacity_dir, fname))

  df <- df %>%
    dplyr::filter(overflow_threshold_percent == 1) %>%
    dplyr::select(geography_modeled, resource_type, avg_resource_available) %>%
    unique() %>%
    pivot_wider(names_from = "resource_type", values_from = "avg_resource_available") %>%
    dplyr::mutate(geography_name = gsub("covidregion_", "", geography_modeled)) %>%
    dplyr::select(geography_name, icu_availforcovid, hb_availforcovid)

  dfRR <- df %>%
    dplyr::rename(region = geography_name) %>%
    f_addRestoreRegion() %>%
    dplyr::group_by(restore_region) %>%
    dplyr::summarize(
      icu_availforcovid = sum(icu_availforcovid),
      hb_availforcovid = sum(hb_availforcovid)
    ) %>%
    dplyr::mutate(geography_name = tolower(restore_region)) %>%
    dplyr::select(geography_name, icu_availforcovid, hb_availforcovid)

  dfIL <- df %>%
    dplyr::summarize(
      icu_availforcovid = sum(icu_availforcovid),
      hb_availforcovid = sum(hb_availforcovid)
    ) %>%
    dplyr::mutate(geography_name = "illinois") %>%
    dplyr::select(geography_name, icu_availforcovid, hb_availforcovid)


  df <- rbind(df, dfRR, dfIL) %>%
    as.data.frame() %>%
    dplyr::rename(
      icu_available = icu_availforcovid,
      medsurg_available = hb_availforcovid
    )

  if (!(is.null(selected_ems))) df <- df %>% filter(geography_name %in% selected_ems)

  return(df)
}


f_aggrDat <- function(dataframe, groupVars, valueVar, WideToLong = FALSE) {
  #' Calculate summary statistic for one variable per specified grouping variables
  #'
  #' The csv file is weekly updated and provided by CIVIS
  #' @param dataframe dataframe with group variables and variable to summarize
  #' @param groupVars vector with names of group variables
  #' @param groupVars vector with names of group variables
  #' @param valueVar name of variable to summarize (cannot take multiple names)
  #' @param WideToLong boolean, if True transforms data from wide to long
  #' 
  ### Aggregate function 
  ## Extended and edited from:
  # https://stackoverflow.com/questions/35953394/calculating-length-of-95-ci-using-dplyr
  library(dplyr)

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


f_weighted.aggrDat <- function(dataframe, groupVars, valueVar, weightVar, WideToLong = FALSE) {
  #' Calculate summary statistic for one variable per specified grouping variables
  #'
  #' The csv file is weekly updated and provided by CIVIS
  #' @param dataframe dataframe with group variables and variable to summarize
  #' @param groupVars vector with names of group variables
  #' @param groupVars vector with names of group variables
  #' @param valueVar name of variable to summarize (cannot take multiple names)
  #' @param weightVar name of weight variable i.e. populations
  #' @param WideToLong boolean, if True transforms data from wide to long
  #' 
  ### Aggregate function 
  ## Extended and edited from:
  # https://stackoverflow.com/questions/35953394/calculating-length-of-95-ci-using-dplyr
  library(dplyr)

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
