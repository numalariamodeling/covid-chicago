
library(rescale)
d_incrSys_lu = c(0, 0.0726 ,0.335 ,0.516 ,0.565 ,0.682, 0.95)
d_incrSys_up = c(0.0185, 0.157 ,0.422 ,0.778 ,0.835 ,0.835,1)

d_Sym_lu = c(0.01, 0.14)
d_Sym_up = c(0.05, 0.17)

d_incrSym_lu = rescale(d_incrSys_lu, to=d_Sym_lu)
d_incrSym_up = rescale(d_incrSys_up, to=d_Sym_up)

dat = as.data.frame(cbind(d_incrSys_up, d_incrSys_lu , d_incrSym_lu, d_incrSym_up))
write.csv(dat)