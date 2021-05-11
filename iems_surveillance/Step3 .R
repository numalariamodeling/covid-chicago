cmd<-commandArgs(trailingOnly = TRUE)
setwd(paste("~/projects/b1139/covidproject/projects/covid_chicago/cms_sim/simulation_output/",cmd,sep = ""))
data1<-read.csv("new_symp_mild.csv")
newdata1<-data1[,8:18]
newdata2<-newdata1
newdata2[,1:11]<-0
for (i in 1:11){
  for (ii in 1:length(newdata1[,i])){
    newdata2[ii,i]<-rbinom(n=1,size=newdata1[ii,i],prob=30/2000)
  }
}

weekdays<-weekdays(as.Date(data1$date))

sumdetected<-rowSums(newdata2)
finalnewdata<-cbind(weekdays,data1[,2:6],sumdetected,newdata2)

trajectory1<-finalnewdata[finalnewdata$scen_num=="1",]
trajectory10<-finalnewdata[finalnewdata$scen_num=="10",]


plot(trajectory1$date,trajectory1$sumdetected)
plot(trajectory10$date,trajectory10$sumdetected)



write.csv(finalnewdata,file="downsampled_cases.csv")
