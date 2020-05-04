
#This script takes hospital data from various EMS regions of Illinois, and compares
##them to simulations where we varied the transmission parameter (Ki), the amount 
#that Ki was reduced during shelter in place, and the start date of the epidemic
#(10 asymptomatic individuals) for each EMS region

#This script assumes that inside simulation output, there is a file
#called EMS_X, where X is a given ems region.
#It assumes that inside that file is a sheet title trajectoriesDat.csv
#It also assumes that in the "data" folder int he "covid_chicago" folder on box
#There are files titled "emresource_by_region.csv", "200428_jg_Admission Date_ems.csv",
#And "200428_jg_Deceased Date_ems.csv".
#The "library(here) call sets the working directoty to be wherever this file lives. 
#For me it lived inside the covid_chicago file in Box (unsynced). If youres lives in git,
#put in a call to set the working directory to the covid_chicago folder on box. 
#Line 233- change working directlory to where you want results saved. 

##set working directory to R.project location
library(here)
library(ggplot2)
library(tidyverse)

##Read in simulations, put in list
sim_ems1 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_1/trajectoriesDat.csv")
sim_ems2 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_2/trajectoriesDat.csv")
sim_ems3 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_3/trajectoriesDat.csv")
sim_ems4 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_4/trajectoriesDat.csv")
sim_ems5 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_5/trajectoriesDat.csv")
sim_ems6 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_6/trajectoriesDat.csv")
sim_ems7 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_7/trajectoriesDat.csv")
sim_ems8 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_8/trajectoriesDat.csv")
sim_ems9 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_9/trajectoriesDat.csv")
sim_ems10 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_10/trajectoriesDat.csv")
sim_ems11 <- read.csv("./covid_chicago/cms_sim/simulation_output/EMS_11/trajectoriesDat.csv")

simulationslist <- list(sim_ems1,sim_ems2,sim_ems3,sim_ems4,sim_ems5,sim_ems6,
                        sim_ems7,sim_ems8,sim_ems9,sim_ems10,sim_ems11)

#read in hospital data
hosp_data <- read.csv("./data/emresource_by_region.csv")

#Replace NA values with zeros (blank in raw data sheet)
hosp_data[is.na(hosp_data)] = 0

#Dates in sheet currently as factor, make as dat
hosp_data$date_of_extract <- as.Date(hosp_data$date_of_extract)

##Separate hospital data by EMS, put in list
hosp_data_ems1 <- hosp_data[which(hosp_data$region == 1),]
hosp_data_ems2 <- hosp_data[which(hosp_data$region == 2),]
hosp_data_ems3 <- hosp_data[which(hosp_data$region == 3),]
hosp_data_ems4 <- hosp_data[which(hosp_data$region == 4),]
hosp_data_ems5 <- hosp_data[which(hosp_data$region == 5),]
hosp_data_ems6 <- hosp_data[which(hosp_data$region == 6),]
hosp_data_ems7 <- hosp_data[which(hosp_data$region == 7),]
hosp_data_ems8 <- hosp_data[which(hosp_data$region == 8),]
hosp_data_ems9 <- hosp_data[which(hosp_data$region == 9),]
hosp_data_ems10 <- hosp_data[which(hosp_data$region == 10),]
hosp_data_ems11 <- hosp_data[which(hosp_data$region == 11),]

hosp_list <- list(hosp_data_ems1,hosp_data_ems2,hosp_data_ems3,hosp_data_ems4,
                  hosp_data_ems5,hosp_data_ems6,hosp_data_ems7,hosp_data_ems8,
                  hosp_data_ems9,hosp_data_ems10,hosp_data_ems11)

#Read in by line hospital admissions data
pre_hosp_adm_data <- read.csv("./data/200428_jg_Admission Date_ems.csv")
#Make date column as date
pre_hosp_adm_data <- pre_hosp_adm_data %>%
  mutate(date = as.Date(date, "%m/%d/%y"))

#Divide by EMS and put in list
pre_hosp_adm_data_ems1 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 1),]
pre_hosp_adm_data_ems2 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 2),]
pre_hosp_adm_data_ems3 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 3),]
pre_hosp_adm_data_ems4 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 4),]
pre_hosp_adm_data_ems5 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 5),]
pre_hosp_adm_data_ems6 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 6),]
pre_hosp_adm_data_ems7 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 7),]
pre_hosp_adm_data_ems8 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 8),]
pre_hosp_adm_data_ems9 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 9),]
pre_hosp_adm_data_ems10 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 10),]
pre_hosp_adm_data_ems11 <- pre_hosp_adm_data[which(pre_hosp_adm_data$EMS == 11),]

pre_hosp_adm_list <- list(pre_hosp_adm_data_ems1,pre_hosp_adm_data_ems2,
                          pre_hosp_adm_data_ems3,pre_hosp_adm_data_ems4,
                          pre_hosp_adm_data_ems5,pre_hosp_adm_data_ems6,
                          pre_hosp_adm_data_ems7,pre_hosp_adm_data_ems8,
                          pre_hosp_adm_data_ems9,pre_hosp_adm_data_ems10,
                          pre_hosp_adm_data_ems11)

#Read in by line hospital death data
pre_hosp_det_data <- read.csv("./data/200428_jg_Deceased Date_ems.csv")
#Make date column as dat
pre_hosp_det_data <- pre_hosp_det_data %>%
  mutate(date = as.Date(date, "%m/%d/%y"))

#Divide by EMS and put in list
pre_hosp_det_data_ems1 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 1),]
pre_hosp_det_data_ems2 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 2),]
pre_hosp_det_data_ems3 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 3),]
pre_hosp_det_data_ems4 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 4),]
pre_hosp_det_data_ems5 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 5),]
pre_hosp_det_data_ems6 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 6),]
pre_hosp_det_data_ems7 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 7),]
pre_hosp_det_data_ems8 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 8),]
pre_hosp_det_data_ems9 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 9),]
pre_hosp_det_data_ems10 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 10),]
pre_hosp_det_data_ems11 <- pre_hosp_det_data[which(pre_hosp_det_data$EMS == 11),]

pre_hosp_det_list <- list(pre_hosp_det_data_ems1,pre_hosp_det_data_ems2,
                          pre_hosp_det_data_ems3,pre_hosp_det_data_ems4,
                          pre_hosp_det_data_ems5,pre_hosp_det_data_ems6,
                          pre_hosp_det_data_ems7,pre_hosp_det_data_ems8,
                          pre_hosp_det_data_ems9,pre_hosp_det_data_ems10,
                          pre_hosp_det_data_ems11)


##loop begin over EMS regions
for(i in 1:11){

#OK, let's prepare the simulation sheet 
sim_ems <- simulationslist[[i]]
sim_ems <- na.omit(sim_ems)

#In the simulations, add a colum for deaths each day rather than cumulative deaths
sim_ems$death_det_24hr <- 0
sim_ems$death_det_24hr[2:length(sim_ems$death_det_24hr)] <- sim_ems$death_det_cumul[2:length(sim_ems$death_det_24hr)] - sim_ems$death_det_cumul[1:(length(sim_ems$death_det_24hr)-1)] 
for(x in 1:length(sim_ems$death_det_24hr)){
  if(sim_ems$time[x] == 0){sim_ems$death_det_24hr[x] <- 0}
}

#Also add a column for new detected symptomatic each day
sim_ems$new_det <- 0
sim_ems$new_det[2:length(sim_ems$new_det)] <- (sim_ems$symp_mild_det_cumul[2:length(sim_ems$symp_mild_det_cumul)] + sim_ems$symp_severe_det_cumul[2:length(sim_ems$symp_severe_det_cumul)]) - 
 (sim_ems$symp_mild_det_cumul[1:(length(sim_ems$symp_mild_det_cumul)-1)] + sim_ems$symp_severe_det_cumul[1:(length(sim_ems$symp_severe_det_cumul)-1)])
for(x in 1:length(sim_ems$new_det)){
  if(sim_ems$time[x] == 0){sim_ems$new_det[x] <- 0}
}

#We need to match simulation dates with real world dates. 
#simulation dates aren't integers, so round them. 
sim_ems$time <- floor(sim_ems$time)

## get EMS specific hosp_data
hosp_data_ems <- hosp_list[[i]]

##get EMS specific admissions data 
pre_hosp_adm_data_ems <- pre_hosp_adm_list[[i]]

#Fill in dates that are missing with 0's
pre_hosp_adm_data_ems <- pre_hosp_adm_data_ems %>%
  complete(date = seq.Date(min(pre_hosp_adm_data_ems$date), max(pre_hosp_adm_data_ems$date), by="day"))
pre_hosp_adm_data_ems$EMS <- i
pre_hosp_adm_data_ems[is.na(pre_hosp_adm_data_ems)] = 0

##get EMS specific death data 
pre_hosp_det_data_ems <- pre_hosp_det_list[[i]]

#Fill in dates that are missing with 0's
pre_hosp_det_data_ems <- pre_hosp_det_data_ems %>%
  complete(date = seq.Date(min(pre_hosp_det_data_ems$date), max(pre_hosp_det_data_ems$date), by="day"))
pre_hosp_det_data_ems$EMS <- i
pre_hosp_det_data_ems[is.na(pre_hosp_det_data_ems)] = 0


##get a list of all scenario numbers run for this EMS
scens <- unique(sim_ems$scen_num)

#create data.frame to hold likelihood results
ems_output <- matrix(0,length(scens),4)
ems_output <- as.data.frame(ems_output)
colnames(ems_output) <- c('Start_date','Ki','Ki_red','NLL')
ems_output$Start_date <- as.Date(ems_output$Start_date, origin = '2020-01-01')

#loop over simulation scenarios and record likelihood
index = 1
for(j in 1:length(scens)){ 
  #pull out all simulation values of given Ki value
  sim_ems_subset <- sim_ems[which(sim_ems$scen_num == scens[j]),]
  #Set the start date to be that based on when we started disease interventions
  sim_ems_subset$time <- as.Date(sim_ems_subset$time,origin = (as.Date("2020-03-12") - floor(sim_ems_subset$socialDistance_time1[1])))
  
  #Get earliest and latest dates of the simualtion data and hopital date
  mindate <- max(min(sim_ems_subset$time),min(hosp_data_ems$date_of_extract))
  maxdate <- min(max(sim_ems_subset$time),max(hosp_data_ems$date_of_extract))
  
  #get rid of dates that don't overlap for comparison'
  sim_ems_subset1 <- sim_ems_subset[which(sim_ems_subset$time >= mindate & sim_ems_subset$time <= maxdate),]
  hosp_data_ems_subset <- hosp_data_ems[which(hosp_data_ems$date_of_extract >= mindate & hosp_data_ems$date_of_extract <= maxdate),]
  
  #Repeat process for simulation data and hosp admission data
  mindate <- max(min(sim_ems_subset$time),min(pre_hosp_adm_data_ems$date))
  maxdate <- min(max(sim_ems_subset$time),max(pre_hosp_adm_data_ems$date))
  
  sim_ems_subset2 <- sim_ems_subset[which(sim_ems_subset$time >= mindate & sim_ems_subset$time <= maxdate),]
  pre_hosp_adm_data_ems_subset <- pre_hosp_adm_data_ems[which(pre_hosp_adm_data_ems$date >= mindate & pre_hosp_adm_data_ems$date <= maxdate),]
  
  #Repeat process for simulation data and hosp death data
  mindate <- max(min(sim_ems_subset$time),min(pre_hosp_det_data_ems$date))
  maxdate <- min(max(sim_ems_subset$time),max(pre_hosp_det_data_ems$date))
  
  sim_ems_subset3 <- sim_ems_subset[which(sim_ems_subset$time >= mindate & sim_ems_subset$time <= maxdate),]
  pre_hosp_det_data_ems_subset <- pre_hosp_det_data_ems[which(pre_hosp_det_data_ems$date >= mindate & pre_hosp_det_data_ems$date <= maxdate),]
  
  
  #Calculate likelyhood
  #Likelyhood of simulation generating detected critical
  nll1 = -1*sum(dpois(hosp_data_ems_subset$confirmed_covid_icu, sim_ems_subset1$crit_det + 1e-10, log=TRUE))
  #Likelyhood of simulation generating detected covid deaths
  nll2 = -1*sum(dpois(hosp_data_ems_subset$confirmed_covid_deaths_prev_24h, sim_ems_subset1$death_det_24hr + 1e-10, log=TRUE))
  #Likelyhood of simulations generating admission data
  nll3 = -1*sum(dpois(pre_hosp_adm_data_ems_subset$cases, sim_ems_subset2$hosp_24hr + 1e-10, log=TRUE))
  #Likelyhood of simulations creating death data that doesn't come from EMresource.
  nll4 = -1*sum(dpois(pre_hosp_det_data_ems_subset$cases, sim_ems_subset$death_det_24hr + 1e-10, log=TRUE))
  #Summ all likelyhood, weighting nll1 and nll2 higher
  nll = nll1 + nll2 + (nll3 + nll4)*(length(hosp_data_ems$confirmed_covid_icu)/length(pre_hosp_adm_data_ems$cases))/2
  
  #Put likelihood values and corresponding start date and Ki in output dataframe
  ems_output$Start_date[index] <- as.Date((as.Date("2020-03-12") - floor(sim_ems_subset$socialDistance_time1[1])))
  ems_output$Ki[index] <- sim_ems_subset$Ki[1]
  ems_output$Ki_red[index]<- sim_ems_subset$social_multiplier_3[1]
  ems_output$NLL[index] <- nll
  
  index = index + 1
}

#Create sheet of the 5% most likely parameter combinations
nam <- paste("ems",i,"_use_values",sep = "")
assign(nam,ems_output[which(ems_output$NLL < quantile(ems_output$NLL,prob=1-95/100)),])

}

##Set working directory to whereever you want results saved. 

#Change to results

#Save best paramter combinations
write.csv(ems1_use_values, "best_parameter_ranges_ems1.csv")
write.csv(ems2_use_values, "best_parameter_ranges_ems2.csv")
write.csv(ems3_use_values, "best_parameter_ranges_ems3.csv")
write.csv(ems4_use_values, "best_parameter_ranges_ems4.csv")
write.csv(ems5_use_values, "best_parameter_ranges_ems5.csv")
write.csv(ems6_use_values, "best_parameter_ranges_ems6.csv")
write.csv(ems7_use_values, "best_parameter_ranges_ems7.csv")
write.csv(ems8_use_values, "best_parameter_ranges_ems8.csv")
write.csv(ems9_use_values, "best_parameter_ranges_ems9.csv")
write.csv(ems10_use_values, "best_parameter_ranges_ems10.csv")
write.csv(ems11_use_values, "best_parameter_ranges_ems11.csv")

#Create figures showing correlations between paramter combinations for 
#Each EMS region
jpeg("Ki_startdate_ems1.jpg")
ggplot(ems1_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems1')
dev.off()

jpeg("Ki_red_startdate_ems1.jpg")
ggplot(ems1_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems1')
dev.off()

jpeg("Ki_Ki_red_ems1.jpg")
ggplot(ems1_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems1')
dev.off()

jpeg("Ki_startdate_ems2.jpg")
ggplot(ems2_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems2')
dev.off()

jpeg("Ki_red_startdate_ems2.jpg")
ggplot(ems2_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems2')
dev.off()

jpeg("Ki_Ki_red_ems2.jpg")
ggplot(ems2_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems2')
dev.off()

jpeg("Ki_startdate_ems3.jpg")
ggplot(ems3_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems3')
dev.off()

jpeg("Ki_red_startdate_ems3.jpg")
ggplot(ems3_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems3')
dev.off()

jpeg("Ki_Ki_red_ems3.jpg")
ggplot(ems3_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems3')
dev.off()

jpeg("Ki_startdate_ems4.jpg")
ggplot(ems4_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems4')
dev.off()

jpeg("Ki_red_startdate_ems4.jpg")
ggplot(ems4_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems4')
dev.off()

jpeg("Ki_Ki_red_ems4.jpg")
ggplot(ems4_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems4')
dev.off()

jpeg("Ki_startdate_ems5.jpg")
ggplot(ems5_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems5')
dev.off()

jpeg("Ki_red_startdate_ems5.jpg")
ggplot(ems5_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems5')
dev.off()

jpeg("Ki_Ki_red_ems5.jpg")
ggplot(ems5_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems5')
dev.off()

jpeg("Ki_startdate_ems6.jpg")
ggplot(ems6_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems6')
dev.off()

jpeg("Ki_red_startdate_ems6.jpg")
ggplot(ems6_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems6')
dev.off()

jpeg("Ki_Ki_red_ems6.jpg")
ggplot(ems6_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems6')
dev.off()

jpeg("Ki_startdate_ems7.jpg")
ggplot(ems7_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems7')
dev.off()

jpeg("Ki_red_startdate_ems7.jpg")
ggplot(ems7_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems7')
dev.off()

jpeg("Ki_Ki_red_ems7.jpg")
ggplot(ems7_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems7')
dev.off()

jpeg("Ki_startdate_ems8.jpg")
ggplot(ems8_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems8')
dev.off()

jpeg("Ki_red_startdate_ems8.jpg")
ggplot(ems8_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems8')
dev.off()

jpeg("Ki_Ki_red_ems8.jpg")
ggplot(ems8_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems8')
dev.off()

jpeg("Ki_startdate_ems9.jpg")
ggplot(ems9_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems9')
dev.off()

jpeg("Ki_red_startdate_ems9.jpg")
ggplot(ems9_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems9')
dev.off()

jpeg("Ki_Ki_red_ems9.jpg")
ggplot(ems9_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems9')
dev.off()

jpeg("Ki_startdate_ems10.jpg")
ggplot(ems10_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems10')
dev.off()

jpeg("Ki_red_startdate_ems10.jpg")
ggplot(ems10_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems10')
dev.off()

jpeg("Ki_Ki_red_ems10.jpg")
ggplot(ems10_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems10')
dev.off()

jpeg("Ki_startdate_ems11.jpg")
ggplot(ems11_use_values,aes(x = Start_date, y = Ki)) +
  geom_point()+
  labs(fill = "NLL")+
  ylim(0,1) + 
  ggtitle('ems11')
dev.off()

jpeg("Ki_red_startdate_ems11.jpg")
ggplot(ems11_use_values,aes(x = Start_date, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") + 
  ggtitle('ems11')
dev.off()

jpeg("Ki_Ki_red_ems11.jpg")
ggplot(ems11_use_values,aes(x = Ki, y = Ki_red)) +
  geom_point()+
  labs(fill = "NLL") +
  xlim(0,1) + 
  ggtitle('ems11')
dev.off()

#Save #1 most likely parameter combination for each region
ems1_best <- ems1_use_values[which(ems1_use_values$NLL == min(ems1_use_values$NLL)),]
ems2_best <- ems2_use_values[which(ems2_use_values$NLL == min(ems2_use_values$NLL)),]
ems3_best <- ems3_use_values[which(ems3_use_values$NLL == min(ems3_use_values$NLL)),]
ems4_best <- ems4_use_values[which(ems4_use_values$NLL == min(ems4_use_values$NLL)),]
ems5_best <- ems5_use_values[which(ems5_use_values$NLL == min(ems5_use_values$NLL)),]
ems6_best <- ems6_use_values[which(ems6_use_values$NLL == min(ems6_use_values$NLL)),]
ems7_best <- ems7_use_values[which(ems7_use_values$NLL == min(ems7_use_values$NLL)),]
ems8_best <- ems8_use_values[which(ems8_use_values$NLL == min(ems8_use_values$NLL)),]
ems9_best <- ems9_use_values[which(ems9_use_values$NLL == min(ems9_use_values$NLL)),]
ems10_best <- ems10_use_values[which(ems10_use_values$NLL == min(ems10_use_values$NLL)),]
ems11_best <- ems11_use_values[which(ems11_use_values$NLL == min(ems11_use_values$NLL)),]

#And show those
ems1_best
ems2_best
ems3_best
ems4_best
ems5_best
ems6_best
ems7_best
ems8_best
ems9_best
ems10_best
ems11_best
