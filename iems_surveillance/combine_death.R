#read file 
#probFile <- read.csv()

deathFile <- read.csv("~/Desktop/total_death_set .csv")
probFile = matrix(runif(25, 0, 1),nrow=5,ncol=5)

#Define variables
x1 = 5; #number of samples
x2 = 5; #number of downsampling levels



#With Mitigation (Set A)
distributionA = data.frame(matrix(, nrow = x1, ncol = x2));
#Create distribution of outcomes
for (i in 1:x1) {
  simDeaths = deathFile$matrix.0..nrow...reps..ncol...1.[i]; 
  for (j in 1:x2){
    weight = probFile[i,j]
    deaths = weight * simDeaths;
    distributionA[i,j] = deaths;
  }
}


#Without Mitigation (Set B)
distributionB = data.frame(matrix(, nrow = x1, ncol = x2));
#Create distribution of outcomes
for (i in 1:x1) {
  simDeaths = deathFile$matrix.0..nrow...reps..ncol...1.[i];
  for (j in 1:x2) {
    weight = 1 - probFile[i,j];
    deaths = weight * simDeaths;
    distributionB[i,j] = deaths;
    }
}

#Combine distribution from Set A and Set B

distributions = distributionA + distributionB;
 
