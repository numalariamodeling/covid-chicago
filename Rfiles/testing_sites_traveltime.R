#########################################################
### Calculate travel time to testing sites in Illinois
#####################################################

## Packages
library(gdistance) # for travel time calculation
library(abind) # for travel time calculation
library(rje) # for travel time calculation
library(ggthemes) # theme for map figures
library(malariaAtlas) # for spatial tool and friction surface
library(tidyverse) # includes ggplot2
library(data.table) # for reading and writing csv files faster
library(pals) # coolwarm color palette
## Plot defaults
theme_set(theme_minimal(base_size = 14))

## Directories
projectDir <- "C:/Users/mrm9534/Box/NU-malaria-team/projects/covid_chicago/"
dataDir <- file.path("C:/Users/mrm9534/Box/NU-malaria-team/data")
shpDir <- file.path(dataDir, "covid_IDPH/shapefiles")
plot_dir <- file.path(projectDir, "Plots + Graphs/testing_sites_traveltime")


get_travel_time <- function(test_sites_csv = "site_coordinates_201026_1.csv") {
  test_sites <- fread(file.path(dataDir, "covid_IDPH", "test_sites", test_sites_csv)) %>%
    rename(X_COORD = W, Y_COORD = N)
  test_sites$nrow <- c(1:nrow(test_sites))
  coordinates(test_sites) <- ~ X_COORD + Y_COORD
  proj4string(test_sites) <- proj4string(IL_sp)
  points <- as.matrix(test_sites@coords)

  # https://medium.com/@abertozz/mapping-travel-times-with-malariaatlas-and-friction-surfaces-f4960f584f08
  ## convert the friction surface to a "transition matrix"
  T <- gdistance::transition(raster_IL, function(x) 1 / mean(x), 8)
  T.GC <- gdistance::geoCorrection(T)

  access.raster <- gdistance::accCost(T.GC, points)

  return(access.raster)
}


## --------------------------------------
###  Load shapefiles and locations
## --------------------------------------
proj_str <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
IL_sp <- shapefile(file.path(shpDir, "covid_regions", "covid_regions.shp")) ## shapefile without lake
IL_sp.f <- as.MAPshp(IL_sp)

surface_title <- "Global friction surface enumerating land-based travel speed with access to motorized transport for a nominal year 2019 "
raster <- malariaAtlas::getRaster(surface = surface_title, shp = IL_sp)
raster_IL <- crop(raster, extent(IL_sp))
raster_IL <- mask(raster_IL, IL_sp)
raster_IL.f <- as.MAPraster(raster_IL)


Apr23 <- get_travel_time(test_sites_csv = "site_coordinates_200423_1.csv")
Jun15 <- get_travel_time(test_sites_csv = "site_coordinates_200615_1.csv")
Oct26 <- get_travel_time(test_sites_csv = "site_coordinates_201026_1.csv")

writeRaster(Apr23, file.path(plot_dir, "travel_time_Apr23.tiff"), overwrite = TRUE)
writeRaster(Jun15, file.path(plot_dir, "travel_time_Jun15.tiff"), overwrite = TRUE)
writeRaster(Oct26, file.path(plot_dir, "travel_time_Oct26.tiff"), overwrite = TRUE)


## --------------------------------------
## Run travel time function and save outputs
## --------------------------------------
rasterdat_Apr23 <- as.MAPraster(Apr23)
rasterdat_Apr23["date"] <- "Apr 23, 2020: 96 sites"
fwrite(rasterdat_Apr23, file.path(plot_dir, "travel_time_Apr23.csv"))

rasterdat_Jun15 <- as.MAPraster(Jun15)
rasterdat_Jun15["date"] <- "Jun 15, 2020: 281 sites"
fwrite(rasterdat_Jun15, file.path(plot_dir, "travel_time_Jun15.csv"))

rasterdat_Oct26 <- as.MAPraster(Oct26)
rasterdat_Oct26["date"] <- "Oct 26,2020: 366 sites"
fwrite(rasterdat_Oct26, file.path(plot_dir, "travel_time_Oct26.csv"))

rasterdat <- rbind(rasterdat_Apr23, rasterdat_Jun15, rasterdat_Oct26) %>% as.data.frame()
summary(rasterdat$z)
rasterdat$z[!is.finite(rasterdat$z)] <- NA
summary(rasterdat$z)
rasterdat$zgrp <- cut(rasterdat$z, c(-Inf, 10, 20, 30, 45, 60, 75, 90, 105, 120, 200),
  labels = c(10, 20, 30, 45, 60, 75, 90, 105, 120, 200)
)
rasterdat$zgrp <- factor(rasterdat$zgrp,
  levels = rev(c(10, 20, 30, 45, 60, 75, 90, 105, 120, 200)),
  labels = rev(c("<10", "10-20", "20-30", "30-45", "45-60", "60-75", "75-90", "90-105", "105-120", ">120"))
)

## --------------------------------------
### Continuous plot
## --------------------------------------
pplot <- ggplot(data = rasterdat) +
  geom_raster(
    aes(x = x, y = y, fill = z),
    alpha = 1
  ) +
  geom_polygon(
    data = IL_sp.f, aes(x = long, y = lat, group = group),
    col = "black", fill = "NA", size = 0.5
  ) +
  # geom_point(data=data.frame(test_sites@coords),
  #           aes(x=X_COORD, y=Y_COORD)) +
  scale_fill_gradientn(colours = coolwarm(100), na.value = NA, breaks = c(0, 30, 60, 90, 120)) +
  # scale_fill_gradient2(low ="#3B4CC0",mid="#ebedf8" , high= "#B40426", na.value=NA, midpoint=30,breaks=c(0,30,60,90,120)) +
  # scale_fill_continuous(palette="RdBu",na.value=NA,) +
  # scale_fill_viridis_c(na.value = NA, direction = -1) +
  labs(
    title = "Travel time to testing site in Illinois",
    caption = "Friction surface obtained from MAP (2019)",
    fill = "Travel time (Minutes)"
  ) +
  theme_map() +
  theme(legend.position = "right") +
  facet_wrap(~date)
print(pplot)

ggsave(paste0("travel_time_colorissue", ".pdf"),
  plot = pplot, path = file.path(plot_dir),
  width = 11, height = 6, device = "pdf"
)
ggsave(paste0("travel_time_colorissue", ".png"),
  plot = pplot, path = file.path(plot_dir),
  width = 11, height = 6, device = "png"
)


## --------------------------------------
### Binned plot
## --------------------------------------
pplot <- ggplot(data = subset(rasterdat, !is.na(zgrp))) +
  geom_raster(
    aes(x = x, y = y, fill = zgrp),
    alpha = 1
  ) +
  geom_polygon(
    data = IL_sp.f, aes(x = long, y = lat, group = group),
    col = "black", fill = "NA", size = 0.5
  ) +
  scale_fill_manual(values = rev(c("#3B4CC0", "#6180E8", "#8CAEFC", "#B7CEF8", "#F49E7F", "#EF896B", "#E47058", "#D65545", "#C63234", "#B40426"))) +
  labs(
    title = "Travel time to testing site in Illinois",
    caption = "Friction surface obtained from MAP (2019)",
    fill = "Travel time (Minutes)"
  ) +
  theme_map() +
  theme(legend.position = "right") +
  facet_wrap(~date)
print(pplot)


ggsave(paste0("travel_time", ".pdf"),
  plot = pplot, path = file.path(plot_dir),
  width = 11, height = 6, device = "pdf"
)
ggsave(paste0("travel_time", ".png"),
  plot = pplot, path = file.path(plot_dir),
  width = 11, height = 6, device = "png"
)

## --------------------------------------
##### Average travel time per CBG
## --------------------------------------
cbg_sp <- shapefile(file.path(shpDir, "tl_2016_17_bg", "tl_2016_17_bg.shp"))
cbg_sp.f <- as.MAPshp(cbg_sp)
cbg_dat <- as.data.frame(cbg_sp)

require(parallel)
tt_labels <- c("Apr23", "Jun15", "Oct26")
tt_rasters <- c(Apr23[[1]], Jun15[[1]], Oct26[[1]])
beginCluster()
tt_values <- list()
for (i in c(1:length(tt_labels))) {
  print(i)
  tt_rasters[i][[1]][!is.finite(tt_rasters[i][[1]])] <- NA
  cbg_dat[paste0("travel_time_min_", tt_labels[i])] <- raster::extract(tt_rasters[i][[1]], cbg_sp, fun = mean, na.rm = TRUE)
}
endCluster()

fwrite(cbg_dat, file.path(plot_dir, "travel_time_perCBG.csv"))

cbg_sp.f <- cbg_sp.f %>% left_join(cbg_dat[, c("GEOID", "travel_time_min_Apr23", "travel_time_min_Jun15", "travel_time_min_Oct26")])

pplot <- ggplot(data = cbg_sp.f) +
  geom_polygon(aes(x = long, y = lat, group = group, fill = travel_time_min_Oct26),
    col = "black", size = 0.01
  ) +
  scale_fill_viridis_c(option = "D") +
  labs(
    title = "Travel time to testing site in Illinois per CBG",
    caption = "Friction surface obtained from MAP (2019)",
    fill = "Travel time (Minutes)"
  ) +
  theme_map() +
  theme(legend.position = "right")
print(pplot)


ggsave(paste0("travel_time_perCBG", ".pdf"),
  plot = pplot, path = file.path(plot_dir),
  width = 5.5, height = 6, device = "pdf"
)
ggsave(paste0("travel_time_perCBG", ".png"),
  plot = pplot, path = file.path(plot_dir),
  width = 5.5, height = 6, device = "png"
)
