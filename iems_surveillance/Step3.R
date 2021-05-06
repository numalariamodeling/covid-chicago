data1<-read.csv("~/Desktop/IEMS394/new_symp_mild.csv")
setwd("~/Desktop/IEMS394")

#newdata1<-round(cbind(data1[,8]*0.1,data1[,9]*0.15,data1[,10]*0.2,data1[,11]*0.17,data1[,12]*0.19,data1[,13]*0.05,data1[,14]*0.23,data1[,15]*0.27,data1[,16]*0.09,data1[,17]*0.16,data1[,18]*0.17))
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




write.csv(finalnewdata,file="data.csv")
