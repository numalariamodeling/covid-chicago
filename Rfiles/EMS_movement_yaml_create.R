
##Last edited 6/1/2020

##This script takes facebook movement data and creates a yaml (text file)
##That has paramters for movement (along with other necessary parameters)

##Se working directory to wherever your Box is. Will need to 
##adjust for individual users
setwd('C:/Users/patri/Desktop/Box_Sync/covid_IDPH/Facebook mobility')

##Load in movement data
 movement <- read.csv('num_to_pop_fromEMS_toEMS.csv') 

##Set working directory to wherever your local github files are stored, 
##To save the yam with the others
setwd('C:/Users/patri/Documents/GitHub/covid-chicago/experiment_configs')
 
##With data we have, it looks like there is no variation in movement over time,
##So we take mean of movement data
ag_move <- aggregate(movement, by = list(movement$fromEMS_toEMS), FUN = mean)  

##In raw data, movement is multiplied by 10000, so create a column without that
ag_move$count_pop <- ag_move$count_10000pop/10000

#Create strings specifying each movement parameter to put in the yaml
#To each EMS, from each EMS
to1_from1 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to1_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_1")],"}")
to1_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_1")],"}")
to1_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_1")],"}")
to1_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_1")],"}")
to1_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_1")],"}")
to1_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_1")],"}")
to1_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_1")],"}")
to1_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_1")],"}")
to1_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_1")],"}")
to1_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_1")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_1")],"}")


to2_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_2")],"}")
to2_from2 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to2_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_2")],"}")
to2_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_2")],"}")
to2_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_2")],"}")
to2_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_2")],"}")
to2_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_2")],"}")
to2_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_2")],"}")
to2_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_2")],"}")
to2_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_2")],"}")
to2_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_2")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_2")],"}")


to3_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_3")],"}")
to3_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_3")],"}")
to3_from3 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to3_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_3")],"}")
to3_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_3")],"}")
to3_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_3")],"}")
to3_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_3")],"}")
to3_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_3")],"}")
to3_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_3")],"}")
to3_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_3")],"}")
to3_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_3")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_3")],"}")


to4_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_4")],"}")
to4_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_4")],"}")
to4_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_4")],"}")
to4_from4 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to4_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_4")],"}")
to4_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_4")],"}")
to4_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_4")],"}")
to4_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_4")],"}")
to4_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_4")],"}")
to4_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_4")],"}")
to4_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_4")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_4")],"}")


to5_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_5")],"}")
to5_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_5")],"}")
to5_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_5")],"}")
to5_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_5")],"}")
to5_from5 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to5_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_5")],"}")
to5_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_5")],"}")
to5_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_5")],"}")
to5_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_5")],"}")
to5_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_5")],"}")
to5_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_5")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_5")],"}")


to6_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_6")],"}")
to6_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_6")],"}")
to6_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_6")],"}")
to6_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_6")],"}")
to6_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_6")],"}")
to6_from6 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to6_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_6")],"}")
to6_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_6")],"}")
to6_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_6")],"}")
to6_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_6")],"}")
to6_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_6")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_6")],"}")


to7_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_7")],"}")
to7_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_7")],"}")
to7_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_7")],"}")
to7_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_7")],"}")
to7_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_7")],"}")
to7_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_7")],"}")
to7_from7 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to7_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_7")],"}")
to7_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_7")],"}")
to7_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_7")],"}")
to7_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_7")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_7")],"}")


to8_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_8")],"}")
to8_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_8")],"}")
to8_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_8")],"}")
to8_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_8")],"}")
to8_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_8")],"}")
to8_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_8")],"}")
to8_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_8")],"}")
to8_from8 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to8_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_8")],"}")
to8_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_8")],"}")
to8_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_8")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_8")],"}")


to9_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_9")],"}")
to9_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_9")],"}")
to9_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_9")],"}")
to9_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_9")],"}")
to9_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_9")],"}")
to9_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_9")],"}")
to9_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_9")],"}")
to9_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_9")],"}")
to9_from9 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to9_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_9")],"}")
to9_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_9")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_9")],"}")


to10_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_10")],"}")
to10_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_10")],"}")
to10_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_10")],"}")
to10_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_10")],"}")
to10_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_10")],"}")
to10_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_10")],"}")
to10_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_10")],"}")
to10_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_10")],"}")
to10_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_10")],"}")
to10_from10 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")
to10_from11 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "11_10")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "11_10")],"}")


to11_from1 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "1_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "1_11")],"}")
to11_from2 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "2_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "2_11")],"}")
to11_from3 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "3_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "3_11")],"}")
to11_from4 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "4_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "4_11")],"}")
to11_from5 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "5_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "5_11")],"}")
to11_from6 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "6_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "6_11")],"}")
to11_from7 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "7_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "7_11")],"}")
to11_from8 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "8_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "8_11")],"}")
to11_from9 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "9_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "9_11")],"}")
to11_from10 <- paste("      - {'low': ",ag_move$count_pop[which(ag_move$Group.1 == "10_11")]," 'high': ",ag_move$count_pop[which(ag_move$Group.1 == "10_11")],"}")
to11_from11 <- paste("      - {'low': ",0.0000," 'high': ",0.0000,"}")


#Create Yaml
fileConn<-file("spatial_EMS_experiment.txt")
writeLines(c("experiment_setup_parameters:
  age_bins:
    - EMS_1
    - EMS_2
    - EMS_3
    - EMS_4
    - EMS_5
    - EMS_6
    - EMS_7
    - EMS_8
    - EMS_9
    - EMS_10
    - EMS_11
fixed_parameters_region_specific:
  N:
    expand_by_age: True
    'IL': [736370,1124941,619366,698886,417674,788985,1814891,1673408,1970275,1052839,2716921]
fixed_parameters_global:
  initialAs:
    expand_by_age: True
    list: [10, 10, 10, 10,10, 9, 10, 10,10,10,10]
  speciesS:
    expand_by_age: True
    custom_function: subtract
    function_kwargs: {'x1': N, 'x2': initialAs}
sampled_parameters:
  social_multiplier_1:
    IL:
      expand_by_age: True
      np.random: uniform
      function_kwargs:
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
        - {'low': 0.7, 'high': 0.9}
  social_multiplier_2:
    IL:
      expand_by_age: True
      np.random: uniform
      function_kwargs:
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5}
        - {'low': 0.2, 'high': 0.5} 
  social_multiplier_3:
    IL:
      expand_by_age: True
      np.random: uniform
      function_kwargs:
        - {'low': 0.220, 'high': 0.220}
        - {'low': 0.132, 'high': 0.132}
        - {'low': 0.240, 'high': 0.240}
        - {'low': 0.103, 'high': 0.103}
        - {'low': 0.195, 'high': 0.195}
        - {'low': 0.090, 'high': 0.090}
        - {'low': 0.122, 'high': 0.122}
        - {'low': 0.100, 'high': 0.100}
        - {'low': 0.105, 'high': 0.105}
        - {'low': 0.118, 'high': 0.118}
        - {'low': 0.100, 'high': 0.100}
  social_multiplier_4:
    IL:
      expand_by_age: True
      np.random: uniform
      function_kwargs:
        - {'low': 0.100, 'high': 0.100}
        - {'low': 0.090, 'high': 0.090}
        - {'low': 0.240, 'high': 0.240}
        - {'low': 0.103, 'high': 0.103}
        - {'low': 0.155, 'high': 0.155}
        - {'low': 0.090, 'high': 0.090}
        - {'low': 0.122, 'high': 0.122}
        - {'low': 0.080, 'high': 0.080}
        - {'low': 0.105, 'high': 0.105}
        - {'low': 0.080, 'high': 0.080}
        - {'low': 0.080, 'high': 0.080}    
  Ki:  
    IL:
      expand_by_age: True
      np.random: uniform
      function_kwargs:
        - {'low': 0.589, 'high': 0.589}
        - {'low': 0.654, 'high': 0.654}
        - {'low': 0.373, 'high': 0.373}
        - {'low': 0.571, 'high': 0.571}
        - {'low': 0.501, 'high': 0.501}
        - {'low': 0.501, 'high': 0.501}
        - {'low': 0.714, 'high': 0.714}
        - {'low': 0.897, 'high': 0.897}
        - {'low': 0.857, 'high': 0.857}
        - {'low': 0.754, 'high': 0.754}
        - {'low': 1.01, 'high': 1.01} ","",
"toEMS_1_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to1_from1,to1_from2,to1_from3,to1_from4,to1_from5,to1_from6,
             to1_from7,to1_from8,to1_from9,to1_from10,to1_from11,"",
"toEMS_2_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to2_from1,to2_from2,to2_from3,to2_from4,to2_from5,to2_from6,
             to2_from7,to2_from8,to2_from9,to2_from10,to2_from11,"",
"toEMS_3_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to3_from1,to3_from2,to3_from3,to3_from4,to3_from5,to3_from6,
             to3_from7,to3_from8,to3_from9,to3_from10,to3_from11,"",
"toEMS_4_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to4_from1,to4_from2,to4_from3,to4_from4,to4_from5,to4_from6,
             to4_from7,to4_from8,to4_from9,to4_from10,to4_from11,"",
"toEMS_5_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to5_from1,to5_from2,to5_from3,to5_from4,to5_from5,to5_from6,
             to5_from7,to5_from8,to5_from9,to5_from10,to5_from11,"",
"toEMS_6_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to6_from1,to6_from2,to6_from3,to6_from4,to6_from5,to6_from6,
             to6_from7,to6_from8,to6_from9,to6_from10,to6_from11,"",
"toEMS_7_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to7_from1,to7_from2,to7_from3,to7_from4,to7_from5,to7_from6,
             to7_from7,to7_from8,to7_from9,to7_from10,to7_from11,"",
"toEMS_8_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to8_from1,to8_from2,to8_from3,to8_from4,to8_from5,to8_from6,
             to8_from7,to8_from8,to8_from9,to8_from10,to8_from11,"",
"toEMS_9_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to9_from1,to9_from2,to9_from3,to9_from4,to9_from5,to9_from6,
             to9_from7,to9_from8,to9_from9,to9_from10,to9_from11,"",
"toEMS_10_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to10_from1,to10_from2,to10_from3,to10_from4,to10_from5,to10_from6,
             to10_from7,to10_from8,to10_from9,to10_from10,to10_from11,"",
"toEMS_11_from:  
  IL:
    expand_by_age: True
    np.random: uniform
    function_kwargs:",to11_from1,to11_from2,to11_from3,to11_from4,to11_from5,to11_from6,
             to11_from7,to11_from8,to11_from9,to11_from10,to11_from11,"",
"  time_infection_import:  # Relative to generic startdate set for IL 
    IL:
      expand_by_age: True
      np.random: uniform
      function_kwargs:
        - {'low': 13.0, 'high': 13.0}
        - {'low': 13.0, 'high': 13.0}
        - {'low': 7.0, 'high':  7.0}
        - {'low': 8.0, 'high':  8.0}
        - {'low': 15.0, 'high': 15.0}
        - {'low': 12.0, 'high': 12.0}
        - {'low': 6.0, 'high':  6.0}
        - {'low': 11.0, 'high':  11.0}
        - {'low': 9.0, 'high': 9.0}
        - {'low': 7.0, 'high':  7.0}
        - {'low': 12.0, 'high':  12.0}    
fitted_parameters:"), fileConn)
close(fileConn)


