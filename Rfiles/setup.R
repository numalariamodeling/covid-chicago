####==================================================
#   Script to manage custom configurations for the project
#   Project: Malaria modelling in Tanzania
#   Manuela Runge, manuela.runge@swisstph.ch
#
####==================================================

## ----packages,------------------------------------------------
#packages_needed <- c( 'readxl', 'broom', 'gsubfn', 'grid', 'tidyverse', 'data.table', 'plyr', 'gridExtra', 'reshape', 'Rmisc',
#                      'iterators', 'RColorBrewer', 'cowplot', 'ggExtra', 'scales', 'raster', 'rworldmap', 'ggmap', 
#                      'rgdal', 'plyr', 'rgeos', 'sp', 'maptools' ,'rdhs', 'srvyr') 
#lapply(packages_needed, require, character.only = TRUE) 



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




### ====================================
### Custom objects frequently used
### ====================================
## positions
pos <- position_dodge(width = 0.9)

### colours
## sequential
TwoCols_seq <- c("#fe9929", "#41b6c4")
ThreeCols_seq <- c("#a1dab4", "#41b6c4", "#225ea8")
FourCols_seq <- c("#fe9929", "#a1dab4", "#41b6c4", "#225ea8")
# FourCols_seq 	= c("#ffffcc", "#a1dab4","#41b6c4","#225ea8")
FiveCols_seq <- c("#ffffcc", "#a1dab4", "#41b6c4", "#225ea8", "green4")
SixCols_seq <- c("#ffffcc", "#a1dab4", "#41b6c4", "#225ea8", "green3", "green4")

### contrast
TwoCols_con <- c("cornflowerblue", "firebrick2")
ThreeCols_con <- c("#fc8d59", "#ffffbf", "#91bfdb") # c("cornflowerblue","firebrick2","green4")
FourCols_con <- c("cornflowerblue", "firebrick2", "green4", "orange")
FiveCols_con <- c("cornflowerblue", "firebrick2", "green4", "orange", "steelblue1")
SixCols_con <- c("cornflowerblue", "darkorange2", "green4", "steelblue1", "#41b6c4", "#984ea3")

## Favourits
TwoCols <- c("deepskyblue2", "darkorange2")
ThreeCols <- c("cornflowerblue", "firebrick2", "green4")
FourCols <- c("#fe9929", "#a1dab4", "#41b6c4", "#225ea8")
FourCols2 <- c("#ffffcc", "#a1dab4", "#41b6c4", "#225ea8")




## ==============================
##### TEXT AND LABELS
## ==============================

customTheme_noAngle <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  plot.title = element_text(size = 20),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 18),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16, angle = 0, hjust = 1),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

customTheme_Angle <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  plot.title = element_text(size = 20),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 18),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 12, angle = 90, hjust = 0, vjust = 0),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

customTheme_noAngle2 <- theme(
  strip.text.x = element_text(size = 16, vjust = -1, hjust = 0),
  strip.background = element_blank(),
  plot.title = element_text(size = 20),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 18),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16, angle = 0, hjust = 0.5),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

customTheme <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 18),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

customThemeNoFacet <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.text.y= element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 16),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

customThemeNoFacet_angle <- theme(
  strip.text.x = element_text(size = 16, face = "bold"),
  strip.background = element_blank(),
  plot.title = element_text(size = 20, vjust = -1, hjust = 0),
  plot.subtitle = element_text(size = 16),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 18),
  legend.text = element_text(size = 16),
  axis.title.x = element_text(size = 18),
  axis.text.x = element_text(size = 16, angle = 45, hjust = 1),
  axis.title.y = element_text(size = 18),
  axis.text.y = element_text(size = 16)
)

## settings for map
map.theme <- theme(
  strip.text.x = element_text(size = 14, vjust = -1, hjust = 0.5, face = "bold"),
  strip.text.y = element_text(size = 14, vjust = -1, hjust = 0.5, face = "bold"),
  strip.background = element_blank(),
  axis.line = element_blank(),
  panel.grid.major = element_blank(),
  panel.grid.minor = element_blank(),
  panel.border = element_blank(),
  panel.background = element_blank(),
  axis.text.x = element_blank(),
  axis.title.x = element_blank(),
  axis.ticks.x = element_blank(),
  axis.title.y = element_blank(),
  axis.text.y = element_blank(),
  axis.ticks.y = element_blank(),
  plot.title = element_text(size = 14, vjust = -1, hjust = 0.5),
  plot.caption = element_text(size = 10),
  legend.title = element_text(size = 12),
  legend.text = element_text(size = 12),
  # legend.key.size	= unit(2.5,"line"),
  legend.position = "right"
)

