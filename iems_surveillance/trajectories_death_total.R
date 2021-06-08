#for calculating total amount of deaths for any Set A/B per X1
#setwd("~/Spring 2021")
traj = read.csv(file = 'trajectoriesDat.csv')
total_time = max(traj$time)
rows = nrow(traj)
reps = rows/total_time
rowVal=0

deaths_setA = data.frame(matrix(0, nrow =reps,ncol= 1))


  
for (i in 1:reps){
  print(i)
  deaths$matrix.0..nrow...reps..ncol...1.[i] = traj$deaths_EMS.11[i*300]
}

write.csv(deaths, file = "total_death_set.csv")
