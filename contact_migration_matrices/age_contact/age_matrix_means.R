#contacts_age_US <- read_excel("Desktop/contacts_age.xlsx", col_names = FALSE)

contact_matrix <- data.frame()
#x ages
contact_matrix[1:4,1] <- rep("U5",4)
contact_matrix[5:8,1] <- rep("age5to9",4)
contact_matrix[9:12,1] <- rep("age20to64",4)
contact_matrix[13:16,1] <- rep("age65",4)
#y ages
contact_matrix[1:16,2] <- rep(c("U5","age5to9","age20to64","age65"),4)
#grab corresponding cols and row for each age interaction
#get mean, min, max
for (i in 1:16){
  if (i >=1 & i <= 4){columns=1}
  else if(i >= 5 & i <= 8){columns=2:4}
  else if(i >= 9 & i <= 12){columns=5:13}
  else if(i >= 13 & i <= 16){columns=14:16}
  if (i ==1 |i ==5|i == 9|i ==13 ){rows=1}
  else if(i ==2 |i ==6|i == 10|i ==14){rows=2:4}
  else if(i ==3 |i ==7|i == 11|i ==15){rows=5:13}
  else if (i ==4 |i ==8|i == 12|i ==16){rows=14:16}
  contact_matrix[i,3] <-mean(unlist(contacts_age_US[rows,columns]))
  contact_matrix[i,4] <- min(contacts_age_US[rows,columns])
  contact_matrix[i,5] <- max(contacts_age_US[rows,columns])
}
colnames(contact_matrix)[1:5] <- c("x","y","mean","lower_limit","upper_limit")

write_csv(contact_matrix,"contact_matrix.csv")
