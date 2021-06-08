# downsampling step
cmd<-commandArgs(trailingOnly = TRUE)
setwd(paste("/projects/b1139/covidproject/projects/covid_chicago/cms_sim/simulation_output/",cmd,sep = ""))
data1<-read.csv("new_symp_mild.csv")
col_name<-"new_symp_mild_EMS.11"
newdata<-0
newdata<-data.frame(matrix(ncol = 5, nrow = 0))
downsample1<-rep(0,50)
downsample2<-rep(0,50)
downsample3<-rep(0,50)
downsample4<-rep(0,50)
downsample5<-rep(0,50)
# prob = downsampling binomial probability
for (i in 1:length(data1[,7])){
  for (j in 1:50){
    downsample1[j]<-rbinom(n=1,size=data1[i,col_name],prob=15/2000)
    downsample2[j]<-rbinom(n=1,size=data1[i,col_name],prob=30/2000)
    downsample3[j]<-rbinom(n=1,size=data1[i,col_name],prob=60/2000)
    downsample4[j]<-rbinom(n=1,size=data1[i,col_name],prob=150/2000)
    downsample5[j]<-rbinom(n=1,size=data1[i,col_name],prob=500/2000)
  }
  replication_num<-c(1:50,1:50,1:50,1:50,1:50)
  #Change region number
  downsampled_EMS11<-c(downsample1,downsample2,downsample3,downsample4,downsample5)
  date<-data.frame(rep(data1[i,6], 250))
  date<-date
  trajectory<-rep(data1[i,3],250)
  downsample_num<-c(rep(1,50),rep(2,50),rep(3,50),rep(4,50),rep(5,50))
  tempdata<-cbind(trajectory,downsample_num,replication_num,date,downsampled_EMS11)
  if (i==1){
    newdata<-tempdata}
  else if (i>1){
    newdata<-rbind(newdata,tempdata)
  }
  
  }

write.csv(newdata,file="downsampled_cases.csv")
 
