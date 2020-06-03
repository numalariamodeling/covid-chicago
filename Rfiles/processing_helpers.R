
#source("load_paths.R")


regions <- list(
  "Northcentral" = c(1, 2),
  "Northeast" = c(7, 8, 9, 10, 11),
  "Central" = c(3, 6),
  "Southern" = c(4, 5),
  "Illinois" = c(1:11)
)


combineDat <- function(filelist, namelist){
  
  count=0
  for (i in c(1:length(filelist))) {
    count=count+1
    dat <- read_csv(file.path(filelist[i]))
    dat$exp_name = namelist[i]
    if(count==1)combinedDat <- dat
    if(count>=1)combinedDat <- rbind(combinedDat, dat)
  }
  return(combinedDat)
}



load_capacity <- function(selected_ems) {
  ems_df <- read_excel(file.path(data_path, "covid_IDPH/Corona virus reports/EMS_report_2020_03_21.xlsx"))
  ems_df <- ems_df %>%
    filter(Date == as.Date("2020-03-27")) %>%
    separate(Region, into = c("ems", "Hospital"), sep = "-") %>%
    mutate(
      hospitalized = `Total_Med/_Surg_Beds`,
      critical = `Total_Adult_ICU_Beds`,
      ventilators = `Total_Vents`
    )
  
  if (length(selected_ems) == 1) {
    capacity <- ems_df %>%
      filter(ems == selected_ems) %>%
      dplyr::select(hospitalized, critical, ventilators)
  } else {
    capacity <- ems_df %>%
      filter(ems %in% selected_ems) %>%
      dplyr::summarize(
        hospitalized = sum(hospitalized),
        critical = sum(critical),
        ventilators = sum(ventilators)
      )
  }
  
  return(capacity)
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
#https://stackoverflow.com/questions/35953394/calculating-length-of-95-ci-using-dplyr

# library(dplyr)

## Custom functions
## To Do: add multiple variables at once ? 

f_aggrDat <- function(dataframe, groupVars, valueVar, WideToLong=FALSE){
  # dataframe = dataframe to aggregate (new datafram will be created)
  # groupVars = variables to aggregate at 
  # valueVar = variable to aggregate 
  # WideToLong = transfrom data to long format, 
  #              so that statistics are in one column instead of spread over rows
  dataframe <- as.data.frame(dataframe)
  dataframe$tempvar <- dataframe[,colnames(dataframe)==valueVar]
  datAggr <- dataframe %>% 
    dplyr::group_by_(.dots=groupVars) %>%
    dplyr::summarise(
      min.val 	= min(tempvar, na.rm = TRUE),
      max.val	= max(tempvar, na.rm = TRUE),
      mean.val 	= mean(tempvar, na.rm = TRUE),
      median.val	= median(tempvar, na.rm = TRUE),
      sd.val		= sd(tempvar, na.rm = TRUE),
      n.val 		= n(),										 
      q25		= quantile(tempvar, probs=0.25, na.rm = TRUE),
      q75		= quantile(tempvar, probs=0.75, na.rm = TRUE),
      q2.5		= quantile(tempvar, probs=0.025, na.rm = TRUE),
      q97.5  	= quantile(tempvar, probs=0.975, na.rm = TRUE)) %>%
    dplyr::mutate(	
      se.val 			= sd.val / sqrt(n.val),
      lower.ci.val 	= mean.val - qt(1 - (0.05 / 2), n.val - 1) * se.val,
      upper.ci.val 	= mean.val + qt(1 - (0.05 / 2), n.val - 1) * se.val,
      weighted=0) %>%
    #dplyr::select(-sd.val, -n.val,-se.val) %>%
    as.data.frame()
  
  if(WideToLong){
    datAggr <- gather(datAggr, -groupVars)
    colnames(datAggr)[colnames(datAggr)=="variable"] <- "statistic" 
    colnames(datAggr)[colnames(datAggr)=="value"] <- valueVar
    datAggr$statistic <- gsub(".val","",datAggr$statistic)
  }
  
  return(datAggr)
}

## keep both names as long as not all scripts are updated
aggrDat <- f_aggrDat

f_weighted.aggrDat <- function(dataframe, groupVars, valueVar, weightVar, WideToLong=FALSE){
  # dataframe = dataframe to aggregate (new datafram will be created)
  # groupVars = variables to aggregate at 
  # valueVar = variable to aggregate 
  # WideToLong = transfrom data to long format, 
  #              so that statistics are in one column instead of spread over rows
  
  dataframe <- as.data.frame(dataframe)
  dataframe$tempvar <- dataframe[,colnames(dataframe)==valueVar]
  dataframe$w <- dataframe[,colnames(dataframe)==weightVar]
  
  datAggr <- dataframe %>% 
    dplyr::group_by_(.dots=groupVars) %>%
    dplyr::summarise(
      min.val 	= min(tempvar, na.rm = TRUE),
      max.val	= max(tempvar, na.rm = TRUE),
      mean.val 	= wt.mean(tempvar, w),
      median.val	= weighted.median(tempvar, w),
      sd.val		= wt.sd(tempvar,w),
      n.val 		= n(),										 
      q25		= weighted.quantile(tempvar,w, probs=0.25),
      q75		= weighted.quantile(tempvar,w, probs=0.75),
      q2.5		= weighted.quantile(tempvar,w, probs=0.025),
      q97.5  	= weighted.quantile(tempvar,w, probs=0.975)) %>%
    dplyr::mutate(	
      se.val 			= sd.val / sqrt(n.val),
      lower.ci.val 	= mean.val - qt(1 - (0.05 / 2), n.val - 1) * se.val,
      upper.ci.val 	= mean.val + qt(1 - (0.05 / 2), n.val - 1) * se.val,
      weighted=1) %>%
    #dplyr::select(-sd.val, -n.val,-se.val) %>%
    as.data.frame()
  
  if(WideToLong){
    datAggr <- gather(datAggr, -groupVars)
    colnames(datAggr)[colnames(datAggr)=="variable"] <- "statistic" 
    colnames(datAggr)[colnames(datAggr)=="value"] <- valueVar
    datAggr$statistic <- gsub(".val","",datAggr$statistic)
  }
  
  return(datAggr)
}