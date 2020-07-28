## Load packages
packages_needed <- c("tidyverse", "cowplot", "scales", "xlsx")
lapply(packages_needed, require, character.only = TRUE)

## Load directories and custom objects and functions
source("load_paths.R")
source("processing_helpers.R")

plot_dir <- file.path(project_path, "Plots + Graphs")
data_path <- file.path(data_path, "covid_IDPH") # covid_IDPH
shp_path <- file.path(data_path, "shapefiles")
map_dir <- file.path(plot_dir, "_trend_tracking", LL_date)
if (!dir.exists(map_dir)) dir.create(map_dir)


#=================================================
#### Save population per covid region 
#=================================================
chicago_pop <- read.csv(file.path(data_path, "EMS Population", "EMS_population_by_county.csv")) %>%
  dplyr::filter(county=="COOK" & EMS ==11) %>%
  dplyr::mutate(county="CHICAGO") %>%
  dplyr::rename(County=county,pop = pop.in.ems ) %>%
  dplyr::select(County, pop)

 county_pop <- read.csv(file.path(data_path, "population", "illinois_pop_by_county.csv")) %>%
   dplyr::mutate(county_name =  toupper(gsub(" County", "", county_name))) %>%
   dplyr::rename(County=county_name ) %>%
   rbind(chicago_pop) %>%
   mutate(pop = ifelse(County =="COOK", pop - chicago_pop$pop, pop))

# county_pop <- read.csv(file.path(data_path, "census/ACS 2018 Estimates By County", "IL Demographics by County - TH.csv")) %>%
#    mutate(county = toupper(gsub(" County","",county )),psource="IL Demographics by County - TH" ) %>% 
#    rename(County=county, pop=population) %>% 
#    dplyr::select(County, pop) %>%
#    rbind(chicago_pop) %>%
#    mutate(pop = ifelse(County =="COOK", pop - chicago_pop$pop, pop))

dim(county_pop)
 
 
restoreRegion <- read_csv(file.path(data_path, "Corona virus reports", "county_restore_region_map.csv"))
restoreRegion <- restoreRegion %>% rename(County = county)

county_pop$County[!(county_pop$County %in% unique(restoreRegion$County))]
unique(restoreRegion$County)[!(unique(restoreRegion$County) %in% county_pop$County)]

covidregion_population_by_county <- county_pop %>%
  as.data.frame() %>%
  left_join(restoreRegion, by = "County")

sum(county_pop$pop)
sum(covidregion_population_by_county$pop) ==sum(county_pop$pop)

write.csv(covidregion_population_by_county, file=file.path(data_path, "EMS Population", "covidregion_population_by_county.csv"), row.names=FALSE)

covid_region_pop <- covidregion_population_by_county %>% 
  dplyr::select(County,new_restore_region,pop) %>% unique() %>% 
  rename(covid_region=new_restore_region) %>%
  group_by(covid_region) %>% 
  summarize(pop=sum(pop)) %>% as.data.frame()

restore_region_pop <- covidregion_population_by_county %>% 
  dplyr::select(County,restore_region,pop) %>% unique() %>% 
  group_by(restore_region) %>% summarize(pop=sum(pop)) %>% as.data.frame()


write.xlsx(covidregion_population_by_county, file=file.path(data_path,"population", "population_source_comparison.xlsx"),  sheetName = "county" , row.names = FALSE)
write.xlsx(covid_region_pop, file=file.path(data_path,"population", "population_source_comparison.xlsx"),  sheetName = "covid_region" , row.names = FALSE, append = TRUE)
write.xlsx(restore_region_pop, file=file.path(data_path,"population", "population_source_comparison.xlsx"),  sheetName = "restore_region" , row.names = FALSE, append = TRUE)


pplot <- read.csv(file.path(data_path, "EMS Population", "covid_region_population_from_RTI.csv")) %>%
  left_join(covid_region_pop, by="covid_region")  %>%
  rename("RTI"=population, "ACS-IDPH"=pop) %>%
  pivot_longer(cols=-c(covid_region)) %>%
  ggplot()+
  theme_cowplot() +
  geom_bar(aes(x=as.factor(covid_region), y=value, fill=name), stat="identity", position="dodge") +
  scale_fill_manual(values=c("orange","deepskyblue3")) +
  scale_y_continuous(labels = number_format(), expand=c(0,0))+
  labs(x="covid region", fill="source", y="total population")


print(pplot)
ggsave(paste0("population_comparison.png"),
       plot = pplot, path = file.path(data_path,"population" ), width = 12, height = 8, device = "png"
)


#=================================================
### Compare population files 
#=================================================
compareSources=FALSE
if(compareSources){
  county_pop1 <- read.csv(file.path(data_path, "population", "illinois_pop_by_county.csv"))
  county_pop2 <- read.csv(file.path(data_path, "EMS Population", "EMS_population_by_county.csv"))
  county_pop3 <- read.csv(file.path(data_path, "census/ACS 2018 Estimates By County", "IL Demographics by County - TH.csv"))
  
  
  read.csv(file.path(data_path, "EMS Population", "EMS_population_by_county.csv")) %>% arrange(county_EMS) %>% 
    group_by(EMS) %>% 
    summarize(share_of_ems_pop=sum(share_of_ems_pop),
              EMS.population=mean(EMS.population))
  
  
  county_pop1 <- county_pop1 %>%
    mutate(county_name = toupper(gsub(" County","",county_name )), psource="illinois_pop_by_county" ) %>% 
    rename(County=county_name)
  
  county_pop2 <- county_pop2 %>%
    mutate(psource="EMS_population_by_county" ) %>%
    mutate(county=gsub("DEWITT","DE WITT",county) ) %>%
    rename(County=county, pop=pop.in.ems) %>% 
    group_by(County,psource) %>%
    summarize(pop=sum(pop))  %>%
    dplyr::select(County, pop,psource)
  
  county_pop3 <- county_pop3 %>%
    mutate(county = toupper(gsub(" County","",county )),psource="IL Demographics by County - TH" ) %>% 
    rename(County=county, pop=population) %>%
    dplyr::select(County, pop,psource)
  
  county_popall <- rbind(county_pop1, county_pop2, county_pop3)
  table(county_popall$psource)
  
  ggplot(data=county_popall) + 
    theme_minimal() +
    geom_point(aes(x=reorder(as.numeric(as.factor(County)),pop), y=pop, col=psource)) +
    coord_flip()
  
  summary(county_popall$pop)
  
  restoreRegion <- read_csv(file.path(data_path, "Corona virus reports", "county_restore_region_map.csv"))
  restoreRegion <- restoreRegion %>% rename(County = county) 
  county_EMS <- read.csv(file.path(data_path, "EMS Population", "EMS_population_by_county.csv")) %>%
    mutate(county=gsub("DEWITT","DE WITT",county) ) %>%
    rename(County=county, EMS_population_by_county=pop.in.ems) %>% 
    dplyr::select(County, EMS, EMS_population_by_county) 
  
  countyPop <- county_popall %>% 
    mutate(psource = ifelse(psource=="EMS_population_by_county", "EMS_population_by_countySum", psource)) %>%
    pivot_wider(names_from="psource", values_from="pop") %>%
    left_join(restoreRegion, by="County") %>%
    left_join(county_EMS, by="County") %>%
    dplyr::select(County, restore_region, new_restore_region, EMS, everything())%>%
    as.data.frame()
  
  #write.csv(countyPop, file=file.path(data_path,"population", "population_source_comparison.csv"), row.names = FALSE)
  
  countyPop <- county_popall %>% 
    mutate(psource = ifelse(psource=="EMS_population_by_county", "EMS_population_by_countySum", psource)) %>%
    pivot_wider(names_from="psource", values_from="pop") %>%
    left_join(restoreRegion, by="County") %>%
    dplyr::select(County, restore_region, new_restore_region, everything())%>%
    as.data.frame()
  
  new_restore_regionPop <- county_popall %>% 
    left_join(restoreRegion, by="County") %>%
    group_by(new_restore_region,psource) %>%
    summarize(pop =sum(pop))%>%
    pivot_wider(names_from="psource", values_from="pop")%>%
    as.data.frame()
  
  #EMS_regionPop <- county_popall %>% 
  #  left_join(restoreRegion, by="County") %>%
  #  group_by(EMS,psource) %>%
  #  summarize(pop =sum(pop))%>%
  #  pivot_wider(names_from="psource", values_from="pop")%>%
  #  as.data.frame()
  
  restore_regionPop <- county_popall %>% 
    left_join(restoreRegion, by="County") %>%
    group_by(restore_region,psource) %>%
    summarize(pop =sum(pop)) %>%
    pivot_wider(names_from="psource", values_from="pop") %>%
    as.data.frame()
  
  
}
